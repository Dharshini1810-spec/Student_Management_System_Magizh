import uuid
from datetime import datetime, date, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from app.api.deps import get_db, get_current_user, RoleRequired
from app.core.permissions import UserRole
from app.core.response import success_response
from app.models.user import User
from app.models.student import Student, AdminStudent, MentorStudent
from app.models.attendance import Attendance, AttendanceRequest
from app.models.todo import Todo
from app.models.project import Project
from app.models.activity_log import ActivityLog
from app.models.notification import Notification
from app.models.daily_content import DailyContent

router = APIRouter()
analytics_router = APIRouter()

def _today() -> date:
    return datetime.now(timezone.utc).date()

def _get_assigned_student_ids(db: Session, admin_id: uuid.UUID = None, mentor_id: uuid.UUID = None):
    q = db.query(Student.id).filter(Student.is_deleted == False)
    if admin_id:
        q = q.join(AdminStudent, AdminStudent.student_id == Student.id).filter(AdminStudent.admin_id == admin_id)
    if mentor_id:
        q = q.join(MentorStudent, MentorStudent.student_id == Student.id).filter(MentorStudent.mentor_id == mentor_id)
    return q

@router.get("/super-admin", response_model=dict)
def get_super_admin_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    today = _today()

    total_users = db.query(User).filter(User.is_deleted == False).count()
    total_admins = db.query(User).filter(User.role == "ADMIN", User.is_deleted == False).count()
    total_mentors = db.query(User).filter(User.role == "MENTOR", User.is_deleted == False).count()
    total_students = db.query(Student).filter(Student.is_deleted == False).count()

    present_today = db.query(Attendance).filter(
        Attendance.date == today, Attendance.status == "PRESENT"
    ).count()
    absent_today = db.query(Attendance).filter(
        Attendance.date == today, Attendance.status == "ABSENT"
    ).count()

    active_projects = db.query(Project).filter(
        Project.status == "in_progress", Project.is_deleted == False
    ).count()

    pending_attendance_requests = db.query(AttendanceRequest).filter(
        AttendanceRequest.status == "PENDING"
    ).count()

    total_todos_completed_today = db.query(Todo).filter(
        Todo.status == "completed", Todo.is_deleted == False,
        cast(Todo.updated_at, Date) == today
    ).count()

    recent_activity_logs = db.query(ActivityLog).order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()

    return success_response(
        data={
            "total_users": total_users,
            "total_admins": total_admins,
            "total_mentors": total_mentors,
            "total_students": total_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "active_projects": active_projects,
            "pending_attendance_requests": pending_attendance_requests,
            "total_todos_completed_today": total_todos_completed_today,
            "recent_activity_logs": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id),
                    "action": log.action,
                    "description": log.description,
                    "entity_type": log.entity_type,
                    "created_at": log.created_at.isoformat()
                }
                for log in recent_activity_logs
            ]
        },
        message="Super Admin dashboard retrieved successfully."
    )

@router.get("/admin", response_model=dict)
def get_admin_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    today = _today()
    admin_id = current_user.id

    assigned_student_ids = _get_assigned_student_ids(db, admin_id=admin_id).subquery()
    my_students = db.query(Student.id).filter(Student.id.in_(assigned_student_ids)).count()

    present_today = db.query(Attendance).filter(
        Attendance.student_id.in_(assigned_student_ids),
        Attendance.date == today, Attendance.status == "PRESENT"
    ).count()
    absent_today = db.query(Attendance).filter(
        Attendance.student_id.in_(assigned_student_ids),
        Attendance.date == today, Attendance.status == "ABSENT"
    ).count()

    pending_attendance_requests = db.query(AttendanceRequest).filter(
        AttendanceRequest.student_id.in_(assigned_student_ids),
        AttendanceRequest.status == "PENDING"
    ).count()

    active_projects = db.query(Project).filter(
        Project.assigned_to.in_(assigned_student_ids),
        Project.status == "in_progress", Project.is_deleted == False
    ).count()

    pending_todos = db.query(Todo).filter(
        Todo.assigned_to.in_(assigned_student_ids),
        Todo.status == "pending", Todo.is_deleted == False
    ).count()

    student_user_ids = db.query(Student.id).filter(Student.id.in_(assigned_student_ids))
    recent_activity = db.query(ActivityLog).filter(
        ActivityLog.user_id.in_(student_user_ids)
    ).order_by(ActivityLog.created_at.desc()).limit(5).all()

    return success_response(
        data={
            "my_students": my_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "pending_attendance_requests": pending_attendance_requests,
            "active_projects": active_projects,
            "pending_todos": pending_todos,
            "recent_activity": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id),
                    "action": log.action,
                    "description": log.description,
                    "created_at": log.created_at.isoformat()
                }
                for log in recent_activity
            ]
        },
        message="Admin dashboard retrieved successfully."
    )

@router.get("/mentor", response_model=dict)
def get_mentor_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.MENTOR])),
    db: Session = Depends(get_db)
):
    today = _today()
    mentor_id = current_user.id

    assigned_student_ids = _get_assigned_student_ids(db, mentor_id=mentor_id).subquery()
    my_students = db.query(Student.id).filter(Student.id.in_(assigned_student_ids)).count()

    present_today = db.query(Attendance).filter(
        Attendance.student_id.in_(assigned_student_ids),
        Attendance.date == today, Attendance.status == "PRESENT"
    ).count()
    absent_today = db.query(Attendance).filter(
        Attendance.student_id.in_(assigned_student_ids),
        Attendance.date == today, Attendance.status == "ABSENT"
    ).count()

    pending_attendance_requests = db.query(AttendanceRequest).filter(
        AttendanceRequest.student_id.in_(assigned_student_ids),
        AttendanceRequest.status == "PENDING"
    ).count()

    active_projects = db.query(Project).filter(
        Project.assigned_to.in_(assigned_student_ids),
        Project.status == "in_progress", Project.is_deleted == False
    ).count()

    pending_todos = db.query(Todo).filter(
        Todo.assigned_to.in_(assigned_student_ids),
        Todo.status == "pending", Todo.is_deleted == False
    ).count()

    student_user_ids = db.query(Student.id).filter(Student.id.in_(assigned_student_ids))
    recent_activity = db.query(ActivityLog).filter(
        ActivityLog.user_id.in_(student_user_ids)
    ).order_by(ActivityLog.created_at.desc()).limit(5).all()

    return success_response(
        data={
            "my_students": my_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "pending_attendance_requests": pending_attendance_requests,
            "active_projects": active_projects,
            "pending_todos": pending_todos,
            "recent_activity": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id),
                    "action": log.action,
                    "description": log.description,
                    "created_at": log.created_at.isoformat()
                }
                for log in recent_activity
            ]
        },
        message="Mentor dashboard retrieved successfully."
    )

@router.get("/student", response_model=dict)
def get_student_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    today = _today()
    student_id = current_user.id

    today_attendance = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == today
    ).first()
    today_attendance_status = today_attendance.status.lower() if today_attendance else "pending"

    my_todos = db.query(Todo).filter(
        Todo.assigned_to == student_id, Todo.is_deleted == False
    ).all()
    todo_total = len(my_todos)
    todo_completed = sum(1 for t in my_todos if t.status == "completed")
    todo_pending = sum(1 for t in my_todos if t.status == "pending")
    todo_in_progress = sum(1 for t in my_todos if t.status == "in_progress")

    my_projects = db.query(Project).filter(
        Project.assigned_to == student_id, Project.is_deleted == False
    ).all()
    project_total = len(my_projects)
    project_completed = sum(1 for p in my_projects if p.status == "completed")
    project_in_progress = sum(1 for p in my_projects if p.status == "in_progress")
    project_not_started = sum(1 for p in my_projects if p.status == "not_started")

    recent_activity = db.query(ActivityLog).filter(
        ActivityLog.user_id == student_id
    ).order_by(ActivityLog.created_at.desc()).limit(5).all()

    unread_notifications = db.query(Notification).filter(
        Notification.user_id == student_id,
        Notification.is_read == False
    ).count()

    today_daily_content = db.query(DailyContent).filter(
        DailyContent.assigned_to == student_id,
        DailyContent.content_date == today,
        DailyContent.is_deleted == False
    ).order_by(DailyContent.created_at.desc()).first()

    return success_response(
        data={
            "today_attendance": today_attendance_status,
            "my_todos": {
                "total": todo_total,
                "completed": todo_completed,
                "pending": todo_pending,
                "in_progress": todo_in_progress
            },
            "my_projects": {
                "total": project_total,
                "completed": project_completed,
                "in_progress": project_in_progress,
                "not_started": project_not_started
            },
            "recent_activity": [
                {
                    "id": str(log.id),
                    "action": log.action,
                    "description": log.description,
                    "entity_type": log.entity_type,
                    "created_at": log.created_at.isoformat()
                }
                for log in recent_activity
            ],
            "unread_notifications": unread_notifications,
            "today_daily_content": {
                "id": str(today_daily_content.id),
                "title": today_daily_content.title,
                "description": today_daily_content.description,
                "links": today_daily_content.links
            } if today_daily_content else None
        },
        message="Student dashboard retrieved successfully."
    )

# ─── Analytics (Super Admin only) ──────────────────────────────────────────────

@analytics_router.get("/attendance-trend", response_model=dict)
def attendance_trend(
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    today = _today()
    thirty_days_ago = today - timedelta(days=29)

    rows = db.query(
        Attendance.date,
        func.count(Attendance.id).label("total")
    ).filter(
        Attendance.date >= thirty_days_ago,
        Attendance.date <= today
    ).group_by(Attendance.date).order_by(Attendance.date).all()

    date_map = {row.date: row.total for row in rows}
    trend = []
    for i in range(30):
        d = thirty_days_ago + timedelta(days=i)
        trend.append({"date": d.isoformat(), "count": date_map.get(d, 0)})

    return success_response(
        data={"trend": trend},
        message="Attendance trend retrieved successfully."
    )

@analytics_router.get("/project-stats", response_model=dict)
def project_stats(
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    rows = db.query(
        Project.status,
        func.count(Project.id).label("count")
    ).filter(Project.is_deleted == False).group_by(Project.status).all()

    stats = {row.status: row.count for row in rows}
    result = {
        "not_started": stats.get("not_started", 0),
        "in_progress": stats.get("in_progress", 0),
        "completed": stats.get("completed", 0)
    }

    return success_response(
        data={"project_stats": result},
        message="Project stats retrieved successfully."
    )

@analytics_router.get("/student-growth", response_model=dict)
def student_growth(
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)

    rows = db.query(
        func.date_trunc("month", User.created_at).label("month"),
        func.count(User.id).label("count")
    ).filter(
        User.role == "STUDENT",
        User.is_deleted == False,
        User.created_at >= six_months_ago
    ).group_by(
        func.date_trunc("month", User.created_at)
    ).order_by(
        func.date_trunc("month", User.created_at)
    ).all()

    growth = [
        {"month": row.month.strftime("%Y-%m"), "count": row.count}
        for row in rows
    ]

    return success_response(
        data={"student_growth": growth},
        message="Student growth retrieved successfully."
    )
