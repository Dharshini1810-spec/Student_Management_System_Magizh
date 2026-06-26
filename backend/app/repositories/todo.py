import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.models.user import User

class TodoRepository:
    @staticmethod
    def create(db: Session, title: str, created_by: uuid.UUID, assigned_to: Optional[uuid.UUID] = None, description: Optional[str] = None, deadline: Optional[datetime] = None, is_personal: bool = False) -> Todo:
        todo = Todo(
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=assigned_to,
            deadline=deadline,
            is_personal=is_personal,
            status="pending"
        )
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo

    @staticmethod
    def get_by_id(db: Session, todo_id: uuid.UUID) -> Optional[Todo]:
        return db.query(Todo).filter(Todo.id == todo_id, Todo.is_deleted == False).first()

    @staticmethod
    def list_by_user(db: Session, user_id: uuid.UUID) -> List[Todo]:
        return db.query(Todo).filter(
            Todo.assigned_to == user_id,
            Todo.is_deleted == False
        ).order_by(Todo.created_at.desc()).all()

    @staticmethod
    def list_created_by(db: Session, user_id: uuid.UUID) -> List[Todo]:
        return db.query(Todo).filter(
            Todo.created_by == user_id,
            Todo.is_deleted == False
        ).order_by(Todo.created_at.desc()).all()

    @staticmethod
    def list_assigned_to_admin(db: Session, admin_id: uuid.UUID) -> List[Todo]:
        from app.models.student import AdminStudent
        assigned_student_ids = db.query(AdminStudent.student_id).filter(AdminStudent.admin_id == admin_id)
        return db.query(Todo).filter(
            Todo.assigned_to.in_(assigned_student_ids),
            Todo.is_deleted == False
        ).order_by(Todo.created_at.desc()).all()

    @staticmethod
    def list_assigned_to_mentor(db: Session, mentor_id: uuid.UUID) -> List[Todo]:
        from app.models.student import MentorStudent
        assigned_student_ids = db.query(MentorStudent.student_id).filter(MentorStudent.mentor_id == mentor_id)
        return db.query(Todo).filter(
            Todo.assigned_to.in_(assigned_student_ids),
            Todo.is_deleted == False
        ).order_by(Todo.created_at.desc()).all()

    @staticmethod
    def list_all(db: Session) -> List[Todo]:
        return db.query(Todo).filter(Todo.is_deleted == False).order_by(Todo.created_at.desc()).all()

    @staticmethod
    def update(db: Session, todo: Todo, update_data: dict) -> Todo:
        for field, value in update_data.items():
            if hasattr(todo, field):
                setattr(todo, field, value)
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo

    @staticmethod
    def soft_delete(db: Session, todo: Todo) -> Todo:
        todo.is_deleted = True
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo

    @staticmethod
    def update_status(db: Session, todo: Todo, status: str) -> Todo:
        todo.status = status
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
