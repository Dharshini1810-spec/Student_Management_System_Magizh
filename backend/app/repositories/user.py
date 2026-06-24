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
            role=role,
            name=name,
            is_first_login=is_first_login,
            is_approved=is_approved,
            is_active=True,
            is_deleted=False,
            admin_id=admin_id,
            mentor_id=mentor_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, db_user: User, update_data: Dict[str, Any]) -> User:
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
            query = query.filter(
                or_(
                    User.mentor_id == mentor_id,
                    User.id == mentor_id
                )
            )
        elif admin_id:
            query = query.filter(
                or_(
                    User.admin_id == admin_id,
                    User.id == admin_id
                )
            )

        # Get total count before limit/offset
        total_count = query.count()

        # Apply pagination
        users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

        return users, total_count

    @staticmethod
    def get_assigned_to_admin(db: Session, admin_id: uuid.UUID) -> list[User]:
        return db.query(User).filter(User.admin_id == admin_id, User.is_deleted == False).all()

    @staticmethod
    def get_assigned_to_mentor(db: Session, mentor_id: uuid.UUID) -> list[User]:
        return db.query(User).filter(User.mentor_id == mentor_id, User.is_deleted == False).all()
