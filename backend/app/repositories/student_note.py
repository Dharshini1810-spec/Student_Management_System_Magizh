import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.student_note import StudentNote

class StudentNoteRepository:
    @staticmethod
    def create(db: Session, student_id: uuid.UUID, written_by: uuid.UUID, content: str) -> StudentNote:
        note = StudentNote(
            student_id=student_id,
            written_by=written_by,
            content=content
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def list_by_student(db: Session, student_id: uuid.UUID) -> List[StudentNote]:
        return db.query(StudentNote).filter(
            StudentNote.student_id == student_id,
            StudentNote.is_deleted == False
        ).order_by(StudentNote.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, note_id: uuid.UUID) -> Optional[StudentNote]:
        return db.query(StudentNote).filter(
            StudentNote.id == note_id,
            StudentNote.is_deleted == False
        ).first()

    @staticmethod
    def soft_delete(db: Session, note: StudentNote) -> StudentNote:
        note.is_deleted = True
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
