import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.project import Project

class ProjectRepository:
    @staticmethod
    def create(db: Session, name: str, assigned_by: uuid.UUID, assigned_to: uuid.UUID, description: Optional[str] = None, tech_stack: Optional[str] = None, deadline: Optional[datetime] = None) -> Project:
        project = Project(
            name=name,
            description=description,
            tech_stack=tech_stack,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            deadline=deadline,
            status="not_started"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_by_id(db: Session, project_id: uuid.UUID) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()

    @staticmethod
    def list_assigned_to(db: Session, user_id: uuid.UUID) -> List[Project]:
        return db.query(Project).filter(
            Project.assigned_to == user_id,
            Project.is_deleted == False
        ).order_by(Project.created_at.desc()).all()

    @staticmethod
    def list_by_assigned_by(db: Session, user_id: uuid.UUID) -> List[Project]:
        return db.query(Project).filter(
            Project.assigned_by == user_id,
            Project.is_deleted == False
        ).order_by(Project.created_at.desc()).all()

    @staticmethod
    def list_assigned_to_admin(db: Session, admin_id: uuid.UUID) -> List[Project]:
        from app.models.student import AdminStudent
        assigned_student_ids = db.query(AdminStudent.student_id).filter(AdminStudent.admin_id == admin_id)
        return db.query(Project).filter(
            Project.assigned_to.in_(assigned_student_ids),
            Project.is_deleted == False
        ).order_by(Project.created_at.desc()).all()

    @staticmethod
    def list_assigned_to_mentor(db: Session, mentor_id: uuid.UUID) -> List[Project]:
        from app.models.student import MentorStudent
        assigned_student_ids = db.query(MentorStudent.student_id).filter(MentorStudent.mentor_id == mentor_id)
        return db.query(Project).filter(
            Project.assigned_to.in_(assigned_student_ids),
            Project.is_deleted == False
        ).order_by(Project.created_at.desc()).all()

    @staticmethod
    def list_all(db: Session) -> List[Project]:
        return db.query(Project).filter(Project.is_deleted == False).order_by(Project.created_at.desc()).all()

    @staticmethod
    def update(db: Session, project: Project, update_data: dict) -> Project:
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def soft_delete(db: Session, project: Project) -> Project:
        project.is_deleted = True
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_status(db: Session, project: Project, status: str) -> Project:
        project.status = status
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
