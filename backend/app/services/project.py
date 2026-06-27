import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from ..core.exceptions import APIException, NotFoundException, AuthorizationException
from ..core.permissions import UserRole
from ..models.user import User
from ..models.project import Project
from ..repositories.project import ProjectRepository


class ProjectService:

    @staticmethod
    def create_project(
        db: Session,
        requester: User,
        name: str,
        assigned_to: uuid.UUID,
        description: Optional[str] = None,
        tech_stack: Optional[str] = None,
        deadline: Optional[datetime] = None,
    ) -> Project:
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value, UserRole.MENTOR.value):
            raise AuthorizationException(
                message="Only Admins, Mentors, or Super Admins can assign projects",
                code="PROJECT_CREATE_FORBIDDEN"
            )

        approval_status = "approved"
        if requester.role == UserRole.MENTOR.value:
            approval_status = "pending"

        return ProjectRepository.create(
            db=db, name=name, assigned_by=requester.id,
            assigned_to=assigned_to, description=description,
            tech_stack=tech_stack, deadline=deadline,
            approval_status=approval_status
        )

    @staticmethod
    def list_projects(db: Session, requester: User) -> List[Project]:
        if requester.role == UserRole.SUPER_ADMIN.value:
            return ProjectRepository.list_all(db)
        elif requester.role == UserRole.ADMIN.value:
            return ProjectRepository.list_assigned_to_admin(db, requester.id)
        elif requester.role == UserRole.MENTOR.value:
            return ProjectRepository.list_assigned_to_mentor(db, requester.id)
        else:
            return ProjectRepository.list_assigned_to_approved(db, requester.id)

    @staticmethod
    def get_project(db: Session, project_id: uuid.UUID) -> Project:
        project = ProjectRepository.get_by_id(db, project_id)
        if not project:
            raise NotFoundException(message=f"Project with id '{project_id}' not found")
        return project

    @staticmethod
    def check_access(requester: User, project: Project) -> None:
        if requester.role == UserRole.SUPER_ADMIN.value:
            return
        if requester.id == project.assigned_by or requester.id == project.assigned_to:
            return
        if requester.role in (UserRole.ADMIN.value, UserRole.MENTOR.value):
            raise AuthorizationException(
                message="You do not have access to this project",
                code="ACCESS_DENIED"
            )
        raise AuthorizationException(
            message="You do not have access to this project",
            code="ACCESS_DENIED"
        )

    @staticmethod
    def update_project(db: Session, requester: User, project_id: uuid.UUID, update_data: dict) -> Project:
        project = ProjectService.get_project(db, project_id)
        if requester.role == UserRole.STUDENT.value:
            raise AuthorizationException(
                message="Students cannot update projects",
                code="PROJECT_UPDATE_FORBIDDEN"
            )
        ProjectService.check_access(requester, project)
        return ProjectRepository.update(db, project, update_data)

    @staticmethod
    def delete_project(db: Session, requester: User, project_id: uuid.UUID) -> Project:
        project = ProjectService.get_project(db, project_id)
        if requester.role == UserRole.STUDENT.value:
            raise AuthorizationException(
                message="Students cannot delete projects",
                code="PROJECT_DELETE_FORBIDDEN"
            )
        ProjectService.check_access(requester, project)
        return ProjectRepository.soft_delete(db, project)

    @staticmethod
    def update_status(db: Session, requester: User, project_id: uuid.UUID, status: str) -> Project:
        project = ProjectService.get_project(db, project_id)
        if requester.id != project.assigned_to:
            raise AuthorizationException(
                message="Only the assigned user can update project status",
                code="PROJECT_STATUS_FORBIDDEN"
            )
        if project.approval_status != "approved":
            raise APIException(
                message="Cannot update status on a project that is not approved",
                code="NOT_APPROVED",
                status_code=400
            )
        if status not in ("not_started", "in_progress", "completed"):
            raise APIException(
                message="Status must be one of: not_started, in_progress, completed",
                code="INVALID_STATUS",
                status_code=400
            )
        return ProjectRepository.update_status(db, project, status)

    @staticmethod
    def list_pending_approval_for_admin(db: Session, admin_id: uuid.UUID) -> List[Project]:
        from app.models.student import AdminStudent
        assigned_student_ids = db.query(AdminStudent.student_id).filter(AdminStudent.admin_id == admin_id)
        return db.query(Project).filter(
            Project.assigned_to.in_(assigned_student_ids),
            Project.approval_status == "pending",
            Project.is_deleted == False
        ).order_by(Project.created_at.desc()).all()

    @staticmethod
    def approve_project(db: Session, requester: User, project_id: uuid.UUID) -> Project:
        project = ProjectService.get_project(db, project_id)
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value):
            raise AuthorizationException(
                message="Only Admins and Super Admins can approve projects",
                code="APPROVAL_FORBIDDEN"
            )
        if project.approval_status != "pending":
            raise APIException(
                message="Project is not pending approval",
                code="NOT_PENDING",
                status_code=400
            )
        return ProjectRepository.update(db, project, {"approval_status": "approved"})

    @staticmethod
    def reject_project(db: Session, requester: User, project_id: uuid.UUID) -> Project:
        project = ProjectService.get_project(db, project_id)
        if requester.role not in (UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value):
            raise AuthorizationException(
                message="Only Admins and Super Admins can reject projects",
                code="REJECTION_FORBIDDEN"
            )
        if project.approval_status != "pending":
            raise APIException(
                message="Project is not pending approval",
                code="NOT_PENDING",
                status_code=400
            )
        return ProjectRepository.update(db, project, {"approval_status": "rejected"})
