import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, RoleRequired
from app.core.permissions import UserRole
from app.core.response import success_response
from app.models.user import User
from app.models.student import Student, AdminStudent, MentorStudent

router = APIRouter()

@router.get("/super-admin", response_model=dict)
def get_super_admin_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Returns global system-wide stats for Super Admins.
    """
    total_users = db.query(User).filter(User.is_deleted == False).count()
    total_admins = db.query(User).filter(User.role == "ADMIN", User.is_deleted == False).count()
    total_mentors = db.query(User).filter(User.role == "MENTOR", User.is_deleted == False).count()
    total_students = db.query(Student).filter(Student.is_deleted == False).count()

    return success_response(
        data={
            "total_users": total_users,
            "total_admins": total_admins,
            "total_mentors": total_mentors,
            "total_students": total_students,
            "present_today": 12,
            "absent_today": 2,
            "active_projects": 6,
            "pending_attendance_requests": 2,
            "completed_todos": 35
        },
        message="Super Admin dashboard retrieved successfully."
    )

@router.get("/admin", response_model=dict)
def get_admin_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Returns dashboard metrics scoped to the Admin's assigned students and mentors.
    """
    admin_id = current_user.id
    
    # Students assigned to this Admin
    assigned_student_ids = db.query(AdminStudent.student_id).filter(AdminStudent.admin_id == admin_id)
    total_students = assigned_student_ids.count()
    
    # Mentors who share these students
    assigned_mentor_ids = db.query(MentorStudent.mentor_id).filter(MentorStudent.student_id.in_(assigned_student_ids)).distinct()
    total_mentors = db.query(User).filter(User.id.in_(assigned_mentor_ids), User.is_deleted == False).count()
    
    total_admins = 1
    total_users = total_students + total_mentors + total_admins
    
    # Realistic scoped mock calculations
    present_today = int(total_students * 0.9)
    absent_today = total_students - present_today
    
    return success_response(
        data={
            "total_users": total_users,
            "total_admins": total_admins,
            "total_mentors": total_mentors,
            "total_students": total_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "active_projects": min(4, total_students),
            "pending_attendance_requests": 1,
            "completed_todos": total_students * 3
        },
        message="Admin dashboard retrieved successfully."
    )

@router.get("/mentor", response_model=dict)
def get_mentor_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.MENTOR])),
    db: Session = Depends(get_db)
):
    """
    Returns dashboard metrics scoped to the Mentor's assigned students.
    """
    mentor_id = current_user.id
    
    # Students assigned to this Mentor
    assigned_student_ids = db.query(MentorStudent.student_id).filter(MentorStudent.mentor_id == mentor_id)
    total_students = assigned_student_ids.count()
    
    # Admins assigned to these students
    assigned_admin_ids = db.query(AdminStudent.admin_id).filter(AdminStudent.student_id.in_(assigned_student_ids)).distinct()
    total_admins = db.query(User).filter(User.id.in_(assigned_admin_ids), User.is_deleted == False).count()
    
    total_mentors = 1
    total_users = total_students + total_mentors + total_admins
    
    present_today = int(total_students * 0.85)
    absent_today = total_students - present_today

    return success_response(
        data={
            "total_users": total_users,
            "total_admins": total_admins,
            "total_mentors": total_mentors,
            "total_students": total_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "active_projects": min(2, total_students),
            "pending_attendance_requests": 1,
            "completed_todos": total_students * 2
        },
        message="Mentor dashboard retrieved successfully."
    )

@router.get("/student", response_model=dict)
def get_student_dashboard(
    current_user: User = Depends(RoleRequired([UserRole.STUDENT])),
    db: Session = Depends(get_db)
):
    """
    Returns dashboard metrics scoped to the Student caller individually.
    """
    student_id = current_user.id
    
    # Admins and Mentors assigned to this Student
    total_admins = db.query(AdminStudent.admin_id).filter(AdminStudent.student_id == student_id).distinct().count()
    total_mentors = db.query(MentorStudent.mentor_id).filter(MentorStudent.student_id == student_id).distinct().count()
    
    total_students = 1
    total_users = total_students + total_admins + total_mentors

    return success_response(
        data={
            "total_users": total_users,
            "total_admins": total_admins,
            "total_mentors": total_mentors,
            "total_students": total_students,
            "present_today": 1,
            "absent_today": 0,
            "active_projects": 1,
            "pending_attendance_requests": 0,
            "completed_todos": 5
        },
        message="Student dashboard retrieved successfully."
    )
