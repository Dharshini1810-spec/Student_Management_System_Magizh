import uuid
from datetime import datetime, date, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, case

from app.api.deps import get_db, get_current_user, PermissionRequired
from app.core.permissions import UserRole
from app.core.response import success_response
from app.models.user import User
from app.models.student import Student, AdminStudent, MentorStudent
from app.models.attendance import Attendance
from app.models.todo import Todo
from app.models.project import Project
from app.models.activity_log import ActivityLog

router = APIRouter()

def _today() -> date:
    return datetime.now(timezone.utc).date()

def _get_assigned_student_ids(db: Session, admin_id: uuid.UUID = None, mentor_id: uuid.UUID = None):
    q = db.query(Student.id).filter(Student.is_deleted == False)
    if admin_id:
        q = q.join(AdminStudent, AdminStudent.student_id == Student.id).filter(AdminStudent.admin_id == admin_id)
    if mentor_id:
        q = q.join(MentorStudent, MentorStudent.student_id == Student.id).filter(MentorStudent.mentor_id == mentor_id)
    return q

def _apply_role_scoping(db: Session, current_user: User):
    if current_user.role == UserRole.SUPER_ADMIN.value:
        return None, None, None
    admin_id = current_user.id if current_user.role == UserRole.ADMIN.value else None
    mentor_id = current_user.id if current_user.role == UserRole.MENTOR.value else None
    student_id = current_user.id if current_user.role == UserRole.STUDENT.value else None
    return admin_id, mentor_id, student_id

def _filtered_student_ids(db: Session, admin_id=None, mentor_id=None, student_id=None):
    if student_id:
        return [student_id]
    if admin_id or mentor_id:
        return [row[0] for row in _get_assigned_student_ids(db, admin_id=admin_id, mentor_id=mentor_id).all()]
    return None

@router.get("/attendance", )
def attendance_report(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(PermissionRequired("reports:view")),
    db: Session = Depends(get_db)
):
    today = _today()
    if not start_date:
        start_date = today - timedelta(days=29)
    if not end_date:
        end_date = today

    admin_id, mentor_id, student_id = _apply_role_scoping(db, current_user)
    student_ids = _filtered_student_ids(db, admin_id, mentor_id, student_id)

    q = db.query(
        Attendance.date,
        func.count(Attendance.id).label("total"),
        func.sum(case((Attendance.status == "PRESENT", 1), else_=0)).label("present"),
        func.sum(case((Attendance.status == "ABSENT", 1), else_=0)).label("absent"),
        func.sum(case((Attendance.status == "LATE", 1), else_=0)).label("late"),
    ).filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    )
    if student_ids is not None:
        q = q.filter(Attendance.student_id.in_(student_ids))
    rows = q.group_by(Attendance.date).order_by(Attendance.date).all()

    report_data = []
    total_present = total_absent = total_late = 0
    for row in rows:
        report_data.append({
            "date": row.date.isoformat(),
            "total": row.total,
            "present": row.present,
            "absent": row.absent,
            "late": row.late,
        })
        total_present += row.present
        total_absent += row.absent
        total_late += row.late

    return success_response(
        data={
            "report": report_data,
            "summary": {
                "total_days": len(report_data),
                "total_present": total_present,
                "total_absent": total_absent,
                "total_late": total_late,
            },
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        },
        message="Attendance report retrieved successfully."
    )

@router.get("/students", )
def student_performance_report(
    current_user: User = Depends(PermissionRequired("reports:view")),
    db: Session = Depends(get_db)
):
    admin_id, mentor_id, student_id = _apply_role_scoping(db, current_user)
    student_ids = _filtered_student_ids(db, admin_id, mentor_id, student_id)

    q = db.query(Student).filter(Student.is_deleted == False)
    if student_ids is not None:
        q = q.filter(Student.id.in_(student_ids))
    students = q.all()

    report_data = []
    for s in students:
        total_todos = db.query(Todo).filter(Todo.assigned_to == s.id, Todo.is_deleted == False).count()
        completed_todos = db.query(Todo).filter(Todo.assigned_to == s.id, Todo.is_deleted == False, Todo.status == "completed").count()
        total_projects = db.query(Project).filter(Project.assigned_to == s.id, Project.is_deleted == False).count()
        completed_projects = db.query(Project).filter(Project.assigned_to == s.id, Project.is_deleted == False, Project.status == "completed").count()
        attendance_total = db.query(Attendance).filter(Attendance.student_id == s.id).count()
        attendance_present = db.query(Attendance).filter(Attendance.student_id == s.id, Attendance.status == "PRESENT").count()

        report_data.append({
            "student_id": str(s.id),
            "name": s.user.name,
            "email": s.user.email,
            "todos": {"total": total_todos, "completed": completed_todos},
            "projects": {"total": total_projects, "completed": completed_projects},
            "attendance": {
                "total": attendance_total,
                "present": attendance_present,
                "attendance_rate": round((attendance_present / attendance_total * 100), 1) if attendance_total > 0 else 0
            }
        })

    return success_response(
        data={"students": report_data},
        message="Student performance report retrieved successfully."
    )

@router.get("/projects", )
def project_report(
    current_user: User = Depends(PermissionRequired("reports:view")),
    db: Session = Depends(get_db)
):
    admin_id, mentor_id, student_id = _apply_role_scoping(db, current_user)
    student_ids = _filtered_student_ids(db, admin_id, mentor_id, student_id)

    q = db.query(Project).filter(Project.is_deleted == False)
    if student_ids is not None:
        q = q.filter(Project.assigned_to.in_(student_ids))
    projects = q.all()

    status_counts = {"not_started": 0, "in_progress": 0, "completed": 0}
    for p in projects:
        if p.status in status_counts:
            status_counts[p.status] += 1

    return success_response(
        data={
            "total_projects": len(projects),
            "status_breakdown": status_counts,
        },
        message="Project report retrieved successfully."
    )

@router.get("/todos", )
def todo_report(
    current_user: User = Depends(PermissionRequired("reports:view")),
    db: Session = Depends(get_db)
):
    admin_id, mentor_id, student_id = _apply_role_scoping(db, current_user)
    student_ids = _filtered_student_ids(db, admin_id, mentor_id, student_id)

    q = db.query(Todo).filter(Todo.is_deleted == False)
    if student_ids is not None:
        q = q.filter(Todo.assigned_to.in_(student_ids))
    todos = q.all()

    status_counts = {"pending": 0, "in_progress": 0, "completed": 0}
    for t in todos:
        if t.status in status_counts:
            status_counts[t.status] += 1

    return success_response(
        data={
            "total_todos": len(todos),
            "status_breakdown": status_counts,
        },
        message="Todo report retrieved successfully."
    )

@router.get("/activity", )
def activity_report(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=500, description="Number of records to return"),
    current_user: User = Depends(PermissionRequired("reports:view")),
    db: Session = Depends(get_db)
):
    today = _today()
    if not start_date:
        start_date = today - timedelta(days=6)
    if not end_date:
        end_date = today

    admin_id, mentor_id, student_id = _apply_role_scoping(db, current_user)
    student_ids = _filtered_student_ids(db, admin_id, mentor_id, student_id)

    q = db.query(ActivityLog).filter(
        cast(ActivityLog.created_at, Date) >= start_date,
        cast(ActivityLog.created_at, Date) <= end_date
    )
    if student_ids is not None:
        q = q.filter(ActivityLog.user_id.in_(student_ids))
    logs = q.order_by(ActivityLog.created_at.desc()).limit(limit).all()

    return success_response(
        data={
            "activity_logs": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id),
                    "action": log.action,
                    "description": log.description,
                    "entity_type": log.entity_type,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ],
            "total": len(logs),
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        },
        message="Activity report retrieved successfully."
    )

@router.get("/summary", )
def comprehensive_summary(
    current_user: User = Depends(PermissionRequired("reports:view")),
    db: Session = Depends(get_db)
):
    admin_id, mentor_id, student_id = _apply_role_scoping(db, current_user)
    student_ids = _filtered_student_ids(db, admin_id, mentor_id, student_id)

    def count_with_scope(model, extra_filters=None):
        q = db.query(func.count(model.id))
        if student_ids is not None and hasattr(model, 'assigned_to'):
            q = q.filter(model.assigned_to.in_(student_ids))
        if student_ids is not None and hasattr(model, 'student_id'):
            q = q.filter(model.student_id.in_(student_ids))
        if extra_filters:
            for f in extra_filters:
                q = q.filter(f)
        return q.scalar()

    total_students = len(student_ids) if student_ids else db.query(Student).filter(Student.is_deleted == False).count()
    total_todos = count_with_scope(Todo, [Todo.is_deleted == False])
    completed_todos = count_with_scope(Todo, [Todo.is_deleted == False, Todo.status == "completed"])
    total_projects = count_with_scope(Project, [Project.is_deleted == False])
    completed_projects = count_with_scope(Project, [Project.is_deleted == False, Project.status == "completed"])
    total_attendance = count_with_scope(Attendance)
    present_attendance = count_with_scope(Attendance, [Attendance.status == "PRESENT"])

    return success_response(
        data={
            "students": {"total": total_students},
            "todos": {"total": total_todos, "completed": completed_todos},
            "projects": {"total": total_projects, "completed": completed_projects},
            "attendance": {
                "total": total_attendance,
                "present": present_attendance,
                "attendance_rate": round((present_attendance / total_attendance * 100), 1) if total_attendance > 0 else 0
            }
        },
        message="Comprehensive summary report retrieved successfully."
    )
