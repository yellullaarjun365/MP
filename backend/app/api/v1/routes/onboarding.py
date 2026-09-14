from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.onboarding import (
    OnboardingFarmRead,
    OnboardingSetupCreate,
)
from app.services import onboarding_service


router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"],
)


@router.post(
    "/setup",
    response_model=OnboardingFarmRead,
    status_code=status.HTTP_201_CREATED,
)
def create_setup(
    data: OnboardingSetupCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return onboarding_service.create_onboarding_setup(
            db,
            owner_id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
