import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionRequired
from app.core.permissions import UserRole
from app.core.exceptions import APIException
from app.core.response import success_response
from app.models.user import User
from app.models.todo import Todo
from app.services.todo import TodoService
from app.schemas.todo import TodoCreate, TodoUpdate, TodoRead, TodoStatusUpdate

router = APIRouter()

def map_todo_to_read(todo: Todo) -> TodoRead:
    return TodoRead(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        assigned_to=todo.assigned_to,
        created_by=todo.created_by,
        created_by_name=todo.creator.name if todo.creator else None,
        assignee_name=todo.assignee.name if todo.assignee else None,
        deadline=todo.deadline,
        status=todo.status,
        is_personal=todo.is_personal,
        is_deleted=todo.is_deleted,
        created_at=todo.created_at,
        updated_at=todo.updated_at
    )

@router.post("", response_model=dict)
def create_todo(
    payload: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = TodoService.create_todo(
        db=db,
        requester=current_user,
        title=payload.title,
        assigned_to=payload.assigned_to,
        description=payload.description,
        deadline=payload.deadline,
        is_personal=False
    )
    return success_response(
        data=map_todo_to_read(todo).model_dump(),
        message="Todo created successfully."
    )

@router.post("/personal", response_model=dict)
def create_personal_todo(
    payload: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STUDENT.value:
        raise APIException(
            message="Only students can create personal todos.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    todo = TodoService.create_todo(
        db=db,
        requester=current_user,
        title=payload.title,
        assigned_to=current_user.id,
        description=payload.description,
        deadline=payload.deadline,
        is_personal=True
    )
    return success_response(
        data=map_todo_to_read(todo).model_dump(),
        message="Personal todo created successfully."
    )

@router.get("", response_model=dict)
def list_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todos = TodoService.list_todos(db=db, requester=current_user)
    todos_data = [map_todo_to_read(t).model_dump() for t in todos]
    return success_response(
        data={"todos": todos_data},
        message="Todos retrieved successfully."
    )

@router.get("/{id}", response_model=dict)
def get_todo(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = TodoService.get_todo(db=db, todo_id=id)
    TodoService.check_access(current_user, todo)
    return success_response(
        data=map_todo_to_read(todo).model_dump(),
        message="Todo retrieved successfully."
    )

@router.put("/{id}", response_model=dict)
def update_todo(
    id: uuid.UUID,
    payload: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = payload.model_dump(exclude_unset=True)
    todo = TodoService.update_todo(
        db=db, requester=current_user,
        todo_id=id, update_data=update_data
    )
    return success_response(
        data=map_todo_to_read(todo).model_dump(),
        message="Todo updated successfully."
    )

@router.patch("/{id}/status", response_model=dict)
def update_todo_status(
    id: uuid.UUID,
    payload: TodoStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = TodoService.update_status(
        db=db, requester=current_user,
        todo_id=id, status=payload.status
    )
    return success_response(
        data=map_todo_to_read(todo).model_dump(),
        message="Todo status updated successfully."
    )

@router.delete("/{id}", response_model=dict)
def delete_todo(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = TodoService.delete_todo(db=db, requester=current_user, todo_id=id)
    return success_response(
        data=map_todo_to_read(todo).model_dump(),
        message="Todo deleted successfully."
    )
