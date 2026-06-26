import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, check_data_access
from app.core.permissions import UserRole
from app.core.exceptions import APIException
from app.core.response import success_response
from app.models.user import User
from app.models.attendance import Attendance, AttendanceRequest, AttendanceSettings
from app.repositories.attendance import AttendanceRepository
from app.repositories.student import StudentRepository
from app.services.activity_log import ActivityLogService
from app.services.notification import NotificationService
from app.schemas.attendance import (
    AttendanceSettingsCreate, AttendanceSettingsRead,
    CheckInRequest, CheckOutRequest,
    AttendanceRead, AttendanceRequestRead
)

router = APIRouter()

def map_attendance_to_read(log: Attendance) -> AttendanceRead:
    return AttendanceRead(
        id=log.id,
        student_id=log.student_id,
        student_name=log.student.user.name if log.student and log.student.user else "Unknown Student",
        date=log.date,
        check_in_time=log.check_in_time,
        check_out_time=log.check_out_time,
        status=log.status,
        is_late_check_in=log.is_late_check_in,
        is_late_check_out=log.is_late_check_out
    )

def map_request_to_read(req: AttendanceRequest) -> AttendanceRequestRead:
    return AttendanceRequestRead(
        id=req.id,
        student_id=req.student_id,
        student_name=req.student.user.name if req.student and req.student.user else "Unknown Student",
        request_type=req.request_type,
        requested_time=req.requested_time,
        reason=req.reason,
        status=req.status,
        reviewed_by=req.reviewed_by,
        reviewed_at=req.reviewed_at,
        created_at=req.created_at
    )

@router.post("/check-in", response_model=dict)
def student_check_in(
    payload: CheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registers a student check-in. Spawns late check-in request if deadline is exceeded.
    """
    if current_user.role != UserRole.STUDENT.value:
        raise APIException(
            message="Only Students can perform check-in.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    attendance, req, result_code = AttendanceRepository.check_in(
        db=db,
        student_id=current_user.id,
        reason=payload.reason
    )

    if result_code == "ALREADY_CHECKED_IN":
        raise APIException(
            message="You have already checked in for today.",
            code="ALREADY_CHECKED_IN",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if result_code == "LATE_REQUEST_PENDING":
        ActivityLogService.log_action(
            db=db, user_id=current_user.id,
            action="ATTENDANCE_LATE_REQUEST",
            description=f"Late check-in request submitted at {datetime.now().strftime('%I:%M %p')}",
            entity_type="attendance_request", entity_id=req.id
        )
        return success_response(
            data={"request": map_request_to_read(req).model_dump(), "status": result_code},
            message="Check-in deadline passed. Late attendance request submitted successfully."
        )

    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="ATTENDANCE_CHECK_IN",
        description=f"Checked in at {attendance.check_in_time.strftime('%I:%M %p')}",
        entity_type="attendance", entity_id=attendance.id
    )
    return success_response(
        data={"attendance": map_attendance_to_read(attendance).model_dump(), "status": result_code},
        message="Checked in successfully."
    )

@router.post("/check-out", response_model=dict)
def student_check_out(
    payload: CheckOutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registers a student check-out. Spawns early departure request if check-out deadline is not met.
    """
    if current_user.role != UserRole.STUDENT.value:
        raise APIException(
            message="Only Students can perform check-out.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    attendance, req, result_code = AttendanceRepository.check_out(
        db=db,
        student_id=current_user.id,
        reason=payload.reason
    )

    if result_code == "LATE_REQUEST_PENDING":
        ActivityLogService.log_action(
            db=db, user_id=current_user.id,
            action="ATTENDANCE_EARLY_DEPARTURE_REQUEST",
            description=f"Early departure request submitted at {datetime.now().strftime('%I:%M %p')}",
            entity_type="attendance_request", entity_id=req.id
        )
        return success_response(
            data={"request": map_request_to_read(req).model_dump(), "status": result_code},
            message="Check-out deadline not reached. Early departure approval request submitted successfully."
        )

    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="ATTENDANCE_CHECK_OUT",
        description=f"Checked out at {attendance.check_out_time.strftime('%I:%M %p')}",
        entity_type="attendance", entity_id=attendance.id
    )
    return success_response(
        data={"attendance": map_attendance_to_read(attendance).model_dump(), "status": result_code},
        message="Checked out successfully."
    )

@router.get("", response_model=dict)
def list_attendance_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists attendance logs scoped by the caller's role.
    """
    admin_id = None
    mentor_id = None
    student_id = None

    if current_user.role == UserRole.ADMIN.value:
        admin_id = current_user.id
    elif current_user.role == UserRole.MENTOR.value:
        mentor_id = current_user.id
    elif current_user.role == UserRole.STUDENT.value:
        student_id = current_user.id

    logs = AttendanceRepository.get_logs(
        db=db,
        admin_id=admin_id,
        mentor_id=mentor_id,
        student_id=student_id
    )

    logs_data = [map_attendance_to_read(log).model_dump() for log in logs]
    return success_response(
        data={"logs": logs_data},
        message="Attendance logs retrieved successfully."
    )

@router.get("/requests", response_model=dict)
def list_attendance_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists late check-in/out approval requests scoped by the caller's role.
    """
    admin_id = None
    mentor_id = None
    student_id = None

    if current_user.role == UserRole.ADMIN.value:
        admin_id = current_user.id
    elif current_user.role == UserRole.MENTOR.value:
        mentor_id = current_user.id
    elif current_user.role == UserRole.STUDENT.value:
        student_id = current_user.id

    requests = AttendanceRepository.get_requests(
        db=db,
        admin_id=admin_id,
        mentor_id=mentor_id,
        student_id=student_id
    )

    reqs_data = [map_request_to_read(req).model_dump() for req in requests]
    return success_response(
        data={"requests": reqs_data},
        message="Attendance requests retrieved successfully."
    )

@router.get("/settings", response_model=dict)
def get_attendance_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gets the current check-in/out deadline settings.
    """
    settings = AttendanceRepository.get_settings(db)
    return success_response(
        data=AttendanceSettingsRead.model_validate(settings).model_dump(),
        message="Attendance settings retrieved successfully."
    )

@router.post("/settings", response_model=dict)
def update_attendance_settings(
    payload: AttendanceSettingsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the deadlines settings. Restricted strictly to Admin or Super Admin.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value]:
        raise APIException(
            message="Only Admins or Super Admins can configure attendance settings.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    settings = AttendanceRepository.save_settings(
        db=db,
        check_in=payload.check_in_deadline,
        check_out=payload.check_out_deadline
    )

    return success_response(
        data=AttendanceSettingsRead.model_validate(settings).model_dump(),
        message="Attendance settings updated successfully."
    )

@router.post("/requests/{id}/approve", response_model=dict)
def approve_attendance_request(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approves a late attendance request. Restricted strictly to Admin or Super Admin.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value]:
        raise APIException(
            message="Only Admins or Super Admins can approve attendance requests.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    req = db.query(AttendanceRequest).filter(AttendanceRequest.id == id).first()
    if not req:
        raise APIException(
            message="Attendance request not found.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Scoping check on target student
    check_data_access(current_user, req.student.user)

    approved_req = AttendanceRepository.approve_request(db, id, current_user.id)
    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="ATTENDANCE_REQUEST_APPROVED",
        description=f"Approved {'check-in' if approved_req.request_type == 'CHECK_IN' else 'check-out'} late request for student",
        entity_type="attendance_request", entity_id=approved_req.id
    )
    request_type_label = "check-in" if approved_req.request_type == "CHECK_IN" else "check-out"
    NotificationService.send_notification(
        db=db, user_id=approved_req.student_id,
        title="Attendance Request Approved",
        message=f"Your late {request_type_label} request has been approved.",
        entity_type="attendance_request", entity_id=approved_req.id
    )
    return success_response(
        data=map_request_to_read(approved_req).model_dump(),
        message="Attendance request approved."
    )

@router.post("/requests/{id}/reject", response_model=dict)
def reject_attendance_request(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rejects a late attendance request. Restricted strictly to Admin or Super Admin.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value]:
        raise APIException(
            message="Only Admins or Super Admins can reject attendance requests.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    req = db.query(AttendanceRequest).filter(AttendanceRequest.id == id).first()
    if not req:
        raise APIException(
            message="Attendance request not found.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Scoping check
    check_data_access(current_user, req.student.user)

    rejected_req = AttendanceRepository.reject_request(db, id, current_user.id)
    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="ATTENDANCE_REQUEST_REJECTED",
        description=f"Rejected {'check-in' if rejected_req.request_type == 'CHECK_IN' else 'check-out'} late request for student",
        entity_type="attendance_request", entity_id=rejected_req.id
    )
    request_type_label = "check-in" if rejected_req.request_type == "CHECK_IN" else "check-out"
    NotificationService.send_notification(
        db=db, user_id=rejected_req.student_id,
        title="Attendance Request Rejected",
        message=f"Your late {request_type_label} request has been rejected.",
        entity_type="attendance_request", entity_id=rejected_req.id
    )
    return success_response(
        data=map_request_to_read(rejected_req).model_dump(),
        message="Attendance request rejected."
    )

@router.get("/{student_id}", response_model=dict)
def get_student_attendance_history(
    student_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the complete attendance history for a specific student.
    """
    student_profile = StudentRepository.get_by_id(db, student_id)
    if not student_profile:
        raise APIException(
            message="Student not found.",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Check caller has permission to view this student's data
    check_data_access(current_user, student_profile.user)

    logs = AttendanceRepository.get_logs(db, student_id=student_id)
    logs_data = [map_attendance_to_read(log).model_dump() for log in logs]
    return success_response(
        data={"logs": logs_data},
        message="Student attendance history retrieved successfully."
    )
