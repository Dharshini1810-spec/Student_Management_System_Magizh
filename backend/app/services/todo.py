import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from ..core.exceptions import APIException, NotFoundException, AuthorizationException
from ..core.permissions import UserRole
from ..models.user import User
from ..models.todo import Todo
from ..repositories.todo import TodoRepository


class TodoService:

    @staticmethod
    def create_todo(
        db: Session,
        requester: User,
        title: str,
        assigned_to: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        deadline: Optional[datetime] = None,
        is_personal: bool = False,
    ) -> Todo:
        if is_personal:
            if requester.role != UserRole.STUDENT.value:
                raise AuthorizationException(
                    message="Only students can create personal todos",
                    code="PERSONAL_TODO_FORBIDDEN"
                )
            return TodoRepository.create(
                db=db, title=title, created_by=requester.id,
                assigned_to=requester.id, description=description,
                deadline=deadline, is_personal=True
            )

        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value, UserRole.MENTOR.value):
            raise AuthorizationException(
                message="Only Admins, Mentors, or Super Admins can assign todos",
                code="TODO_CREATE_FORBIDDEN"
            )

        approval_status = "approved"
        if requester.role == UserRole.MENTOR.value:
            approval_status = "pending"

        return TodoRepository.create(
            db=db, title=title, created_by=requester.id,
            assigned_to=assigned_to, description=description,
            deadline=deadline, is_personal=False,
            approval_status=approval_status
        )

    @staticmethod
    def list_todos(db: Session, requester: User) -> List[Todo]:
        if requester.role == UserRole.SUPER_ADMIN.value:
            return TodoRepository.list_all(db)
        elif requester.role == UserRole.ADMIN.value:
            return TodoRepository.list_assigned_to_admin(db, requester.id)
        elif requester.role == UserRole.MENTOR.value:
            return TodoRepository.list_assigned_to_mentor(db, requester.id)
        else:
            return TodoRepository.list_assigned_to_user_approved(db, requester.id)

    @staticmethod
    def get_todo(db: Session, todo_id: uuid.UUID) -> Todo:
        todo = TodoRepository.get_by_id(db, todo_id)
        if not todo:
            raise NotFoundException(message=f"Todo with id '{todo_id}' not found")
        return todo

    @staticmethod
    def check_access(requester: User, todo: Todo) -> None:
        if requester.role == UserRole.SUPER_ADMIN.value:
            return
        if requester.id == todo.created_by or requester.id == todo.assigned_to:
            return
        if requester.role == UserRole.ADMIN.value or requester.role == UserRole.MENTOR.value:
            raise AuthorizationException(
                message="You do not have access to this todo",
                code="ACCESS_DENIED"
            )
        raise AuthorizationException(
            message="You do not have access to this todo",
            code="ACCESS_DENIED"
        )

    @staticmethod
    def update_todo(db: Session, requester: User, todo_id: uuid.UUID, update_data: dict) -> Todo:
        todo = TodoService.get_todo(db, todo_id)
        if requester.role == UserRole.STUDENT.value:
            raise AuthorizationException(
                message="Students cannot update todos",
                code="TODO_UPDATE_FORBIDDEN"
            )
        TodoService.check_access(requester, todo)
        return TodoRepository.update(db, todo, update_data)

    @staticmethod
    def delete_todo(db: Session, requester: User, todo_id: uuid.UUID) -> Todo:
        todo = TodoService.get_todo(db, todo_id)
        if requester.role == UserRole.STUDENT.value:
            raise AuthorizationException(
                message="Students cannot delete todos",
                code="TODO_DELETE_FORBIDDEN"
            )
        TodoService.check_access(requester, todo)
        return TodoRepository.soft_delete(db, todo)

    @staticmethod
    def update_status(db: Session, requester: User, todo_id: uuid.UUID, status: str) -> Todo:
        todo = TodoService.get_todo(db, todo_id)
        if requester.id != todo.assigned_to:
            raise AuthorizationException(
                message="Only the assigned user can update todo status",
                code="TODO_STATUS_FORBIDDEN"
            )
        if todo.approval_status != "approved":
            raise APIException(
                message="Cannot update status on a todo that is not approved",
                code="NOT_APPROVED",
                status_code=400
            )
        if status not in ("pending", "in_progress", "completed"):
            raise APIException(
                message="Status must be one of: pending, in_progress, completed",
                code="INVALID_STATUS",
                status_code=400
            )
        return TodoRepository.update_status(db, todo, status)

    @staticmethod
    def list_pending_approval_for_admin(db: Session, admin_id: uuid.UUID) -> List[Todo]:
        from app.models.student import AdminStudent
        assigned_student_ids = db.query(AdminStudent.student_id).filter(AdminStudent.admin_id == admin_id)
        return db.query(Todo).filter(
            Todo.assigned_to.in_(assigned_student_ids),
            Todo.approval_status == "pending",
            Todo.is_deleted == False
        ).order_by(Todo.created_at.desc()).all()

    @staticmethod
    def approve_todo(db: Session, requester: User, todo_id: uuid.UUID) -> Todo:
        todo = TodoService.get_todo(db, todo_id)
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value):
            raise AuthorizationException(
                message="Only Admins and Super Admins can approve todos",
                code="APPROVAL_FORBIDDEN"
            )
        if todo.approval_status != "pending":
            raise APIException(
                message="Todo is not pending approval",
                code="NOT_PENDING",
                status_code=400
            )
        return TodoRepository.update(db, todo, {"approval_status": "approved"})

    @staticmethod
    def reject_todo(db: Session, requester: User, todo_id: uuid.UUID) -> Todo:
        todo = TodoService.get_todo(db, todo_id)
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value):
            raise AuthorizationException(
                message="Only Admins and Super Admins can reject todos",
                code="REJECTION_FORBIDDEN"
            )
        if todo.approval_status != "pending":
            raise APIException(
                message="Todo is not pending approval",
                code="NOT_PENDING",
                status_code=400
            )
        return TodoRepository.update(db, todo, {"approval_status": "rejected"})
