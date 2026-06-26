import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, check_data_access
from app.core.permissions import UserRole
from app.core.exceptions import APIException, NotFoundException
from app.core.response import success_response
from app.models.user import User
from app.models.student_note import StudentNote
from app.repositories.user import UserRepository
from app.repositories.student_note import StudentNoteRepository
from app.schemas.student_note import StudentNoteCreate, StudentNoteRead

router = APIRouter()

def map_note_to_read(note: StudentNote) -> StudentNoteRead:
    return StudentNoteRead(
        id=note.id,
        student_id=note.student_id,
        written_by=note.written_by,
        content=note.content,
        author_name=note.author.name if note.author else None,
        is_deleted=note.is_deleted,
        created_at=note.created_at,
        updated_at=note.updated_at
    )

def require_admin_or_mentor(current_user: User) -> None:
    if current_user.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value, UserRole.MENTOR.value):
        raise APIException(
            message="Only Admins, Mentors, or Super Admins can access student notes.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

@router.post("", response_model=dict)
def create_student_note(
    student_id: uuid.UUID,
    payload: StudentNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin_or_mentor(current_user)

    target_user = UserRepository.get_by_id(db, student_id)
    if not target_user or target_user.role != UserRole.STUDENT.value:
        raise APIException(
            message="Student not found.",
            code="NOT_FOUND",
            status_code=404
        )

    check_data_access(current_user, target_user, db)

    note = StudentNoteRepository.create(
        db=db,
        student_id=student_id,
        written_by=current_user.id,
        content=payload.content
    )
    return success_response(
        data=map_note_to_read(note).model_dump(),
        message="Note added successfully."
    )

@router.get("", response_model=dict)
def list_student_notes(
    student_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin_or_mentor(current_user)

    target_user = UserRepository.get_by_id(db, student_id)
    if not target_user or target_user.role != UserRole.STUDENT.value:
        raise APIException(
            message="Student not found.",
            code="NOT_FOUND",
            status_code=404
        )

    check_data_access(current_user, target_user, db)

    notes = StudentNoteRepository.list_by_student(db, student_id)
    notes_data = [map_note_to_read(n).model_dump() for n in notes]
    return success_response(
        data={"notes": notes_data},
        message="Notes retrieved successfully."
    )

@router.delete("/{note_id}", response_model=dict)
def delete_student_note(
    student_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin_or_mentor(current_user)

    target_user = UserRepository.get_by_id(db, student_id)
    if not target_user or target_user.role != UserRole.STUDENT.value:
        raise APIException(
            message="Student not found.",
            code="NOT_FOUND",
            status_code=404
        )

    check_data_access(current_user, target_user, db)

    note = StudentNoteRepository.get_by_id(db, note_id)
    if not note:
        raise APIException(
            message="Note not found.",
            code="NOT_FOUND",
            status_code=404
        )

    if note.student_id != student_id:
        raise APIException(
            message="Note does not belong to this student.",
            code="MISMATCH",
            status_code=400
        )

    if current_user.role != UserRole.SUPER_ADMIN.value and note.written_by != current_user.id:
        raise APIException(
            message="You can only delete your own notes.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    StudentNoteRepository.soft_delete(db, note)
    return success_response(
        message="Note deleted successfully."
    )
