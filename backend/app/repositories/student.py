import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.models.student import Student, AdminStudent, MentorStudent
from app.models.user import User

class StudentRepository:
    @staticmethod
    def get_by_id(db: Session, student_id: uuid.UUID) -> Optional[Student]:
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def get_all(
        db: Session,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        include_deleted: bool = False,
        admin_id: Optional[uuid.UUID] = None,
        mentor_id: Optional[uuid.UUID] = None,
        student_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Student], int]:
        # Start query joining User
        query = db.query(Student).join(User, Student.id == User.id)

        # Soft delete filter on Student/User
        if not include_deleted:
            query = query.filter(Student.is_deleted == False, User.is_deleted == False)

        # Active filter (on User table)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Search query (User's name or email, or Student's nickname/position)
        if search_query:
            search_clean = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_clean),
                    User.email.ilike(search_clean),
                    Student.nickname.ilike(search_clean),
                    Student.position.ilike(search_clean)
                )
            )

        # Scoping filters
        if student_id:
            query = query.filter(Student.id == student_id)
        elif mentor_id:
            query = query.join(MentorStudent, MentorStudent.student_id == Student.id)\
                         .filter(MentorStudent.mentor_id == mentor_id)
        elif admin_id:
            query = query.join(AdminStudent, AdminStudent.student_id == Student.id)\
                         .filter(AdminStudent.admin_id == admin_id)

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination and sorting
        students = query.order_by(Student.date_joined.desc()).offset(offset).limit(limit).all()

        return students, total_count

    @staticmethod
    def create_profile(
        db: Session,
        student_id: uuid.UUID,
        nickname: Optional[str] = None,
        dob: Optional[datetime] = None,
        contact: Optional[str] = None,
        position: Optional[str] = None,
        avatar: Optional[str] = None
    ) -> Student:
        student = Student(
            id=student_id,
            nickname=nickname,
            dob=dob,
            contact=contact,
            position=position,
            avatar=avatar,
            is_deleted=False
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def update_profile(
        db: Session,
        db_student: Student,
        update_data: Dict[str, Any]
    ) -> Student:
        # Some update_data fields might belong to the User model (name, email, is_active)
        user_fields = ["name", "email", "is_active"]
        user_update = {}
        
        for field in list(update_data.keys()):
            if field in user_fields:
                user_update[field] = update_data.pop(field)

        # Update User fields if any
        if user_update:
            for field, value in user_update.items():
                if field == "email" and value:
                    value = value.lower().strip()
                setattr(db_student.user, field, value)
            db.add(db_student.user)

        # Update Student fields
        for field, value in update_data.items():
            if hasattr(db_student, field):
                setattr(db_student, field, value)
        
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student

    @staticmethod
    def assign_admin(db: Session, student_id: uuid.UUID, admin_id: uuid.UUID) -> AdminStudent:
        # Check if already assigned
        existing = db.query(AdminStudent).filter(
            AdminStudent.student_id == student_id,
            AdminStudent.admin_id == admin_id
        ).first()
        if existing:
            return existing

        assoc = AdminStudent(admin_id=admin_id, student_id=student_id)
        db.add(assoc)
        db.commit()
        db.refresh(assoc)
        return assoc

    @staticmethod
    def assign_mentor(db: Session, student_id: uuid.UUID, mentor_id: uuid.UUID) -> MentorStudent:
        # Check if already assigned
        existing = db.query(MentorStudent).filter(
            MentorStudent.student_id == student_id,
            MentorStudent.mentor_id == mentor_id
        ).first()
        if existing:
            return existing

        assoc = MentorStudent(mentor_id=mentor_id, student_id=student_id)
        db.add(assoc)
        db.commit()
        db.refresh(assoc)
        return assoc
