import uuid
from typing import Optional, List, Tuple
from datetime import datetime, date, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.attendance import Attendance, AttendanceRequest, AttendanceSettings
from app.models.student import Student, AdminStudent, MentorStudent
from app.models.user import User

class AttendanceRepository:
    @staticmethod
    def get_settings(db: Session) -> AttendanceSettings:
        settings = db.query(AttendanceSettings).first()
        if not settings:
            settings = AttendanceSettings(check_in_deadline="09:00", check_out_deadline="17:00")
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings

    @staticmethod
    def save_settings(db: Session, check_in: str, check_out: str) -> AttendanceSettings:
        settings = AttendanceRepository.get_settings(db)
        settings.check_in_deadline = check_in
        settings.check_out_deadline = check_out
        db.add(settings)
        db.commit()
        db.refresh(settings)
        return settings

    @staticmethod
    def check_in(db: Session, student_id: uuid.UUID, reason: Optional[str] = None) -> Tuple[Optional[Attendance], Optional[AttendanceRequest], str]:
        settings = AttendanceRepository.get_settings(db)
        now_local = datetime.now()
        current_time_str = now_local.strftime("%H:%M")
        today = now_local.date()

        # Check if already checked in today
        existing = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.date == today
        ).first()

        if existing and existing.check_in_time is not None:
            return existing, None, "ALREADY_CHECKED_IN"

        # Check if late check-in deadline has passed
        if current_time_str > settings.check_in_deadline:
            # Create a late check-in request
            req = AttendanceRequest(
                student_id=student_id,
                request_type="CHECK_IN",
                requested_time=now_local,
                reason=reason,
                status="PENDING"
            )
            db.add(req)
            db.commit()
            db.refresh(req)
            return None, req, "LATE_REQUEST_PENDING"
        else:
            # Check-in on time
            if existing:
                existing.check_in_time = now_local
                existing.status = "PRESENT"
                attendance = existing
            else:
                attendance = Attendance(
                    student_id=student_id,
                    date=today,
                    check_in_time=now_local,
                    status="PRESENT",
                    is_late_check_in=False
                )
            db.add(attendance)
            db.commit()
            db.refresh(attendance)
            return attendance, None, "SUCCESS"

    @staticmethod
    def check_out(db: Session, student_id: uuid.UUID, reason: Optional[str] = None) -> Tuple[Optional[Attendance], Optional[AttendanceRequest], str]:
        settings = AttendanceRepository.get_settings(db)
        now_local = datetime.now()
        current_time_str = now_local.strftime("%H:%M")
        today = now_local.date()

        # Check if attendance record exists for today
        existing = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.date == today
        ).first()

        # Check if check-out deadline has passed (early departure check)
        if current_time_str < settings.check_out_deadline:
            # Requires an early/late check-out request
            req = AttendanceRequest(
                student_id=student_id,
                request_type="CHECK_OUT",
                requested_time=now_local,
                reason=reason,
                status="PENDING"
            )
            db.add(req)
            db.commit()
            db.refresh(req)
            return None, req, "LATE_REQUEST_PENDING"
        else:
            # Check-out on time
            if not existing:
                # If they didn't check in, create log but status is LATE or PRESENT
                attendance = Attendance(
                    student_id=student_id,
                    date=today,
                    check_out_time=now_local,
                    status="PRESENT",
                    is_late_check_out=False
                )
            else:
                existing.check_out_time = now_local
                attendance = existing

            db.add(attendance)
            db.commit()
            db.refresh(attendance)
            return attendance, None, "SUCCESS"

    @staticmethod
    def approve_request(db: Session, request_id: uuid.UUID, reviewer_id: uuid.UUID) -> AttendanceRequest:
        req = db.query(AttendanceRequest).filter(AttendanceRequest.id == request_id).first()
        if not req:
            raise ValueError("Request not found.")
        
        req.status = "APPROVED"
        req.reviewed_by = reviewer_id
        req.reviewed_at = datetime.now()
        
        # Apply to attendance logs
        req_date = req.requested_time.date()
        attendance = db.query(Attendance).filter(
            Attendance.student_id == req.student_id,
            Attendance.date == req_date
        ).first()
        
        if not attendance:
            attendance = Attendance(
                student_id=req.student_id,
                date=req_date,
                status="LATE" if req.request_type == "CHECK_IN" else "PRESENT"
            )
            
        if req.request_type == "CHECK_IN":
            attendance.check_in_time = req.requested_time
            attendance.is_late_check_in = True
            attendance.status = "LATE"
        else:
            attendance.check_out_time = req.requested_time
            attendance.is_late_check_out = True

        db.add(attendance)
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def reject_request(db: Session, request_id: uuid.UUID, reviewer_id: uuid.UUID) -> AttendanceRequest:
        req = db.query(AttendanceRequest).filter(AttendanceRequest.id == request_id).first()
        if not req:
            raise ValueError("Request not found.")
        
        req.status = "REJECTED"
        req.reviewed_by = reviewer_id
        req.reviewed_at = datetime.now()
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def get_requests(
        db: Session,
        admin_id: Optional[uuid.UUID] = None,
        mentor_id: Optional[uuid.UUID] = None,
        student_id: Optional[uuid.UUID] = None
    ) -> List[AttendanceRequest]:
        query = db.query(AttendanceRequest)
        
        if student_id:
            query = query.filter(AttendanceRequest.student_id == student_id)
        elif mentor_id:
            query = query.join(MentorStudent, MentorStudent.student_id == AttendanceRequest.student_id)\
                         .filter(MentorStudent.mentor_id == mentor_id)
        elif admin_id:
            query = query.join(AdminStudent, AdminStudent.student_id == AttendanceRequest.student_id)\
                         .filter(AdminStudent.admin_id == admin_id)
                         
        return query.order_by(AttendanceRequest.created_at.desc()).all()

    @staticmethod
    def get_logs(
        db: Session,
        admin_id: Optional[uuid.UUID] = None,
        mentor_id: Optional[uuid.UUID] = None,
        student_id: Optional[uuid.UUID] = None
    ) -> List[Attendance]:
        query = db.query(Attendance)
        
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        elif mentor_id:
            query = query.join(MentorStudent, MentorStudent.student_id == Attendance.student_id)\
                         .filter(MentorStudent.mentor_id == mentor_id)
        elif admin_id:
            query = query.join(AdminStudent, AdminStudent.student_id == Attendance.student_id)\
                         .filter(AdminStudent.admin_id == admin_id)
                         
        return query.order_by(Attendance.date.desc()).all()
