import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, PermissionRequired, check_data_access
from app.core.permissions import UserRole
from app.core.security import get_password_hash
from app.core.exceptions import APIException
from app.core.response import success_response
from app.models.student import Student
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate, StudentRead, AdminAssign, MentorAssign

router = APIRouter()

DEFAULT_STANDARD_PASSWORD = "StandardPassword123!"

def map_student_to_read(student: Student) -> StudentRead:
    assigned_admin_ids = [admin.id for admin in student.assigned_admins]
    assigned_mentor_ids = [mentor.id for mentor in student.assigned_mentors]
    
    return StudentRead(
        id=student.id,
        name=student.user.name,
        email=student.user.email,
        role=student.user.role,
        is_active=student.user.is_active,
        is_deleted=student.is_deleted,
        nickname=student.nickname,
        dob=student.dob,
        contact=student.contact,
        position=student.position,
        avatar=student.avatar,
        date_joined=student.date_joined,
        assigned_admin_id=assigned_admin_ids[0] if assigned_admin_ids else None,
        assigned_mentor_id=assigned_mentor_ids[0] if assigned_mentor_ids else None,
        assigned_admin_ids=assigned_admin_ids,
        assigned_mentor_ids=assigned_mentor_ids
    )

@router.get("", response_model=dict)
def list_students(
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_deleted: bool = False,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists students with support for pagination, search, active filters, and soft-delete visibility.
    Enforces role scoping (Super Admin see all, Admin see assigned, Mentor see assigned, Student see self).
    """
    # Enforce general view permission (or allow Student to view themselves)
    # Check permissions dynamically
    is_student_caller = current_user.role == UserRole.STUDENT.value

    # Scoping variables
    admin_id = None
    mentor_id = None
    student_id = None

    if current_user.role == UserRole.ADMIN.value:
        admin_id = current_user.id
    elif current_user.role == UserRole.MENTOR.value:
        mentor_id = current_user.id
    elif is_student_caller:
        student_id = current_user.id

    students, total_count = StudentRepository.get_all(
        db=db,
        search_query=search,
        is_active=is_active,
        include_deleted=include_deleted,
        admin_id=admin_id,
        mentor_id=mentor_id,
        student_id=student_id,
        limit=limit,
        offset=offset
    )

    students_data = [map_student_to_read(s).model_dump() for s in students]

    return success_response(
        data={
            "students": students_data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        },
        message="Students retrieved successfully."
    )

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: StudentCreate,
    current_user: User = Depends(PermissionRequired("students:create")),
    db: Session = Depends(get_db)
):
    """
    Creates a new Student user and their associated profile.
    Automatically assigns the creator Admin if applicable.
    """
    existing_user = UserRepository.get_by_email(db, student_in.email)
    if existing_user:
        raise APIException(
            message="Email is already in use.",
            code="EMAIL_ALREADY_IN_USE",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # Hash password
    password = student_in.password or DEFAULT_STANDARD_PASSWORD
    hashed_pw = get_password_hash(password)

    # Create the user (Student role). The DB hook also creates the Student profile.
    user = UserRepository.create(
        db=db,
        email=student_in.email,
        hashed_password=hashed_pw,
        role="STUDENT",
        name=student_in.name,
        is_first_login=True,
        is_approved=True
    )

    # Retrieve student profile and update extra profile fields
    student = StudentRepository.get_by_id(db, user.id)
    if student:
        extra_fields = student_in.model_dump(exclude={"name", "email", "password"}, exclude_none=True)
        if extra_fields:
            student = StudentRepository.update_profile(db, student, extra_fields)

    # Automatic assignment if creator is Admin
    if current_user.role == UserRole.ADMIN.value:
        StudentRepository.assign_admin(db, user.id, current_user.id)

    return success_response(
        data=map_student_to_read(student).model_dump(),
        message="Student created successfully."
    )

@router.get("/{id}", response_model=dict)
def get_student(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves student details by ID. Scoping check is enforced.
    """
    student = StudentRepository.get_by_id(db, id)
    if not student:
        raise APIException(
            message="Student not found.",
            code="STUDENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    check_data_access(current_user, student.user)

    return success_response(
        data=map_student_to_read(student).model_dump(),
        message="Student retrieved successfully."
    )

@router.put("/{id}", response_model=dict)
def update_student(
    id: uuid.UUID,
    student_in: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates student profile and user details.
    """
    student = StudentRepository.get_by_id(db, id)
    if not student:
        raise APIException(
            message="Student not found.",
            code="STUDENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    check_data_access(current_user, student.user)

    # If they are not editing their own details, require students:update permission
    if current_user.id != student.id:
        # Dynamically check permissions
        PermissionRequired("students:update")(current_user, db)

    update_data = student_in.model_dump(exclude_none=True)
    student = StudentRepository.update_profile(db, student, update_data)

    return success_response(
        data=map_student_to_read(student).model_dump(),
        message="Student profile updated successfully."
    )

@router.delete("/{id}", response_model=dict)
def delete_student(
    id: uuid.UUID,
    current_user: User = Depends(PermissionRequired("students:delete")),
    db: Session = Depends(get_db)
):
    """
    Soft deletes a student.
    """
    student = StudentRepository.get_by_id(db, id)
    if not student:
        raise APIException(
            message="Student not found.",
            code="STUDENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    check_data_access(current_user, student.user)

    # Soft delete
    student.is_deleted = True
    student.user.is_deleted = True
    db.add(student)
    db.add(student.user)
    db.commit()

    return success_response(
        data={},
        message="Student soft deleted successfully."
    )

@router.post("/{id}/assign-admin", response_model=dict)
def assign_student_admin(
    id: uuid.UUID,
    payload: AdminAssign,
    current_user: User = Depends(PermissionRequired("students:update")),
    db: Session = Depends(get_db)
):
    """
    Assigns a student to an Admin.
    """
    student = StudentRepository.get_by_id(db, id)
    if not student:
        raise APIException(
            message="Student not found.",
            code="STUDENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    admin_user = UserRepository.get_by_id(db, payload.admin_id)
    if not admin_user or admin_user.role != UserRole.ADMIN.value:
        raise APIException(
            message="Target user is not a valid Admin.",
            code="INVALID_ADMIN",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    StudentRepository.assign_admin(db, id, payload.admin_id)
    return success_response(
        data=map_student_to_read(student).model_dump(),
        message="Student assigned to Admin successfully."
    )

@router.post("/{id}/assign-mentor", response_model=dict)
def assign_student_mentor(
    id: uuid.UUID,
    payload: MentorAssign,
    current_user: User = Depends(PermissionRequired("students:update")),
    db: Session = Depends(get_db)
):
    """
    Assigns a student to a Mentor.
    """
    student = StudentRepository.get_by_id(db, id)
    if not student:
        raise APIException(
            message="Student not found.",
            code="STUDENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    mentor_user = UserRepository.get_by_id(db, payload.mentor_id)
    if not mentor_user or mentor_user.role != UserRole.MENTOR.value:
        raise APIException(
            message="Target user is not a valid Mentor.",
            code="INVALID_MENTOR",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    StudentRepository.assign_mentor(db, id, payload.mentor_id)
    return success_response(
        data=map_student_to_read(student).model_dump(),
        message="Student assigned to Mentor successfully."
    )
