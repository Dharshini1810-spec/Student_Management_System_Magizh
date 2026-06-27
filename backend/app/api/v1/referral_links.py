import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.response import success_response
from app.core.exceptions import APIException
from app.models.user import User
from app.schemas.referral_link import ReferralLinkCreate, ReferralLinkUpdate, ReferralLinkRead
from app.services.referral_link import ReferralLinkService
from starlette import status

router = APIRouter()

def map_to_read(link, db: Session = None) -> dict:
    return ReferralLinkRead(
        id=link.id,
        user_id=link.user_id,
        code=link.code,
        description=link.description,
        is_active=link.is_active,
        max_uses=link.max_uses,
        current_uses=link.current_uses,
        expires_at=link.expires_at,
        created_at=link.created_at,
        user_name=link.user.name if link.user else None
    ).model_dump()

@router.post("", response_model=dict)
def create_referral_link(
    payload: ReferralLinkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    link = ReferralLinkService.create_link(
        db=db, requester=current_user,
        description=payload.description,
        max_uses=payload.max_uses,
        expires_at=payload.expires_at
    )
    return success_response(data=map_to_read(link), message="Referral link created.")

@router.get("", response_model=dict)
def list_referral_links(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    links = ReferralLinkService.list_links(db=db, requester=current_user)
    return success_response(data={"links": [map_to_read(l) for l in links]}, message="Referral links retrieved.")

@router.get("/{id}", response_model=dict)
def get_referral_link(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    link = ReferralLinkService.get_link(db=db, link_id=id)
    return success_response(data=map_to_read(link), message="Referral link retrieved.")

@router.delete("/{id}", response_model=dict)
def deactivate_referral_link(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    link = ReferralLinkService.deactivate_link(db=db, requester=current_user, link_id=id)
    return success_response(data=map_to_read(link), message="Referral link deactivated.")
