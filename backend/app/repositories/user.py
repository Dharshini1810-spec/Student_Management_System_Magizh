import uuid
from typing import Optional, Any, Dict, List, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def get_by_reset_token(db: Session, token: str) -> Optional[User]:
        return db.query(User).filter(User.reset_token == token).first()

    @staticmethod
    def create(
        db: Session,
        email: str,
        hashed_password: str,
        role: str,
        name: Optional[str] = None,
        is_first_login: bool = True,
        is_approved: bool = True,
        admin_id: Optional[uuid.UUID] = None,
        mentor_id: Optional[uuid.UUID] = None
    ) -> User:
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            role=role.upper(),
            name=name,
            is_first_login=is_first_login,
            is_approved=is_approved,
            is_active=True,
            is_deleted=False
        )
        db.add(user)
        db.flush()

        if role.upper() == "STUDENT":
            from app.models.student import Student, AdminStudent, MentorStudent
            student_profile = Student(id=user.id)
            db.add(student_profile)
            db.flush()

            if admin_id:
                admin_assoc = AdminStudent(admin_id=admin_id, student_id=user.id)
                db.add(admin_assoc)
            if mentor_id:
                mentor_assoc = MentorStudent(mentor_id=mentor_id, student_id=user.id)
                db.add(mentor_assoc)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, db_user: User, update_data: Dict[str, Any]) -> User:
        from app.models.student import Student, AdminStudent, MentorStudent
        
        # Intercept admin_id and mentor_id for students
        if db_user.role == "STUDENT":
            if "admin_id" in update_data:
                admin_id = update_data.pop("admin_id")
                db.query(AdminStudent).filter(AdminStudent.student_id == db_user.id).delete()
                if admin_id:
                    db.add(AdminStudent(admin_id=admin_id, student_id=db_user.id))
            if "mentor_id" in update_data:
                mentor_id = update_data.pop("mentor_id")
                db.query(MentorStudent).filter(MentorStudent.student_id == db_user.id).delete()
                if mentor_id:
                    db.add(MentorStudent(mentor_id=mentor_id, student_id=db_user.id))

        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_all(
        db: Session,
        role: Optional[str] = None,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        include_deleted: bool = False,
        admin_id: Optional[uuid.UUID] = None,
        mentor_id: Optional[uuid.UUID] = None,
        student_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[User], int]:
        query = db.query(User)

        # Soft delete filter
        if not include_deleted:
            query = query.filter(User.is_deleted == False)

        # Role filter
        if role:
            query = query.filter(User.role == role.upper())

        # Active filter
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Search query (name or email)
        if search_query:
            search_query_clean = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_query_clean),
                    User.email.ilike(search_query_clean)
                )
            )

        # Scoping filters
        if student_id:
            query = query.filter(User.id == student_id)
        elif mentor_id:
            from app.models.student import MentorStudent
            assigned_student_ids = db.query(MentorStudent.student_id).filter(MentorStudent.mentor_id == mentor_id)
            query = query.filter(
                or_(
                    User.id == mentor_id,
                    User.id.in_(assigned_student_ids)
                )
            )
        elif admin_id:
            from app.models.student import AdminStudent, MentorStudent
            assigned_student_ids = db.query(AdminStudent.student_id).filter(AdminStudent.admin_id == admin_id)
            assigned_mentor_ids = db.query(MentorStudent.mentor_id).filter(MentorStudent.student_id.in_(assigned_student_ids))
            query = query.filter(
                or_(
                    User.id == admin_id,
                    User.id.in_(assigned_student_ids),
                    User.id.in_(assigned_mentor_ids)
                )
            )

        # Get total count before limit/offset
        total_count = query.count()

        # Apply pagination
        users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

        return users, total_count

    @staticmethod
    def get_assigned_to_admin(db: Session, admin_id: uuid.UUID) -> list[User]:
        from app.models.student import AdminStudent
        return db.query(User).join(AdminStudent, AdminStudent.student_id == User.id).filter(
            AdminStudent.admin_id == admin_id,
            User.is_deleted == False
        ).all()

    @staticmethod
    def get_assigned_to_mentor(db: Session, mentor_id: uuid.UUID) -> list[User]:
        from app.models.student import MentorStudent
        return db.query(User).join(MentorStudent, MentorStudent.student_id == User.id).filter(
            MentorStudent.mentor_id == mentor_id,
            User.is_deleted == False
        ).all()
