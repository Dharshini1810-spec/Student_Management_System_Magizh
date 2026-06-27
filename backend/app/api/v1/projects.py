import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.permissions import UserRole
from app.core.exceptions import APIException
from app.core.response import success_response
from app.models.user import User
from app.models.project import Project
from app.services.project import ProjectService
from app.services.activity_log import ActivityLogService
from app.services.notification import NotificationService
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectStatusUpdate, ProjectApprovalUpdate
from starlette import status

router = APIRouter()

def map_project_to_read(project: Project) -> ProjectRead:
    return ProjectRead(
        id=project.id,
        name=project.name,
        description=project.description,
        tech_stack=project.tech_stack,
        assigned_to=project.assigned_to,
        assigned_by=project.assigned_by,
        assignee_name=project.assignee.name if project.assignee else None,
        assigner_name=project.assigner.name if project.assigner else None,
        deadline=project.deadline,
        status=project.status,
        approval_status=project.approval_status,
        is_deleted=project.is_deleted,
        created_at=project.created_at,
        updated_at=project.updated_at
    )

@router.post("", response_model=dict)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = ProjectService.create_project(
        db=db,
        requester=current_user,
        name=payload.name,
        assigned_to=payload.assigned_to,
        description=payload.description,
        tech_stack=payload.tech_stack,
        deadline=payload.deadline
    )
    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="PROJECT_CREATED",
        description=f"Created project: {project.name}",
        entity_type="project", entity_id=project.id
    )
    if payload.assigned_to:
        NotificationService.send_notification(
            db=db, user_id=payload.assigned_to,
            title="Project Assigned",
            message=f"You have been assigned a project: {project.name}",
            entity_type="project", entity_id=project.id
        )
    return success_response(
        data=map_project_to_read(project).model_dump(),
        message="Project created successfully."
    )

@router.get("", response_model=dict)
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = ProjectService.list_projects(db=db, requester=current_user)
    projects_data = [map_project_to_read(p).model_dump() for p in projects]
    return success_response(
        data={"projects": projects_data},
        message="Projects retrieved successfully."
    )

@router.get("/{id}", response_model=dict)
def get_project(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = ProjectService.get_project(db=db, project_id=id)
    ProjectService.check_access(current_user, project)
    return success_response(
        data=map_project_to_read(project).model_dump(),
        message="Project retrieved successfully."
    )

@router.put("/{id}", response_model=dict)
def update_project(
    id: uuid.UUID,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = payload.model_dump(exclude_unset=True)
    project = ProjectService.get_project(db=db, project_id=id)
    old_assigned_to = project.assigned_to
    project = ProjectService.update_project(
        db=db, requester=current_user,
        project_id=id, update_data=update_data
    )
    if "assigned_to" in update_data and update_data["assigned_to"] and update_data["assigned_to"] != old_assigned_to:
        NotificationService.send_notification(
            db=db, user_id=update_data["assigned_to"],
            title="Project Assigned",
            message=f"You have been assigned a project: {project.name}",
            entity_type="project", entity_id=project.id
        )
    return success_response(
        data=map_project_to_read(project).model_dump(),
        message="Project updated successfully."
    )

@router.patch("/{id}/status", response_model=dict)
def update_project_status(
    id: uuid.UUID,
    payload: ProjectStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = ProjectService.update_status(
        db=db, requester=current_user,
        project_id=id, status=payload.status
    )
    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="PROJECT_STATUS_UPDATED",
        description=f"Updated project '{project.name}' status to {payload.status}",
        entity_type="project", entity_id=project.id
    )
    return success_response(
        data=map_project_to_read(project).model_dump(),
        message="Project status updated successfully."
    )

@router.get("/pending-approval", response_model=dict)
def list_pending_approval_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.SUPER_ADMIN.value:
        from app.repositories.project import ProjectRepository
        all_projects = ProjectRepository.list_all(db)
        pending = [p for p in all_projects if p.approval_status == "pending"]
    elif current_user.role == UserRole.ADMIN.value:
        pending = ProjectService.list_pending_approval_for_admin(db, current_user.id)
    else:
        raise APIException(
            message="Only Admins and Super Admins can view pending approvals",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )
    return success_response(
        data={"projects": [map_project_to_read(p).model_dump() for p in pending]},
        message="Pending approval projects retrieved."
    )

@router.patch("/{id}/approve", response_model=dict)
def approve_project(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = ProjectService.approve_project(db=db, requester=current_user, project_id=id)
    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="PROJECT_APPROVED",
        description=f"Approved project: {project.name}",
        entity_type="project", entity_id=project.id
    )
    if project.assigned_to:
        NotificationService.send_notification(
            db=db, user_id=project.assigned_to,
            title="Project Approved",
            message=f"Your project '{project.name}' has been approved.",
            entity_type="project", entity_id=project.id
        )
    if project.assigned_by:
        NotificationService.send_notification(
            db=db, user_id=project.assigned_by,
            title="Project Approved",
            message=f"The project '{project.name}' you created has been approved.",
            entity_type="project", entity_id=project.id
        )
    return success_response(
        data=map_project_to_read(project).model_dump(),
        message="Project approved successfully."
    )

@router.patch("/{id}/reject", response_model=dict)
def reject_project(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = ProjectService.reject_project(db=db, requester=current_user, project_id=id)
    ActivityLogService.log_action(
        db=db, user_id=current_user.id,
        action="PROJECT_REJECTED",
        description=f"Rejected project: {project.name}",
        entity_type="project", entity_id=project.id
    )
    if project.assigned_by:
        NotificationService.send_notification(
            db=db, user_id=project.assigned_by,
            title="Project Rejected",
            message=f"The project '{project.name}' has been rejected.",
            entity_type="project", entity_id=project.id
        )
    return success_response(
        data=map_project_to_read(project).model_dump(),
        message="Project rejected successfully."
    )

@router.delete("/{id}", response_model=dict)
def delete_project(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = ProjectService.delete_project(db=db, requester=current_user, project_id=id)
    return success_response(
        data=map_project_to_read(project).model_dump(),
        message="Project deleted successfully."
    )
