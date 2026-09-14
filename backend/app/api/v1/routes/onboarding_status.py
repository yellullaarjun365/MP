from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.onboarding_status import OnboardingStatusRead
from app.services import onboarding_status_service


router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"],
)


@router.get(
    "/status",
    response_model=OnboardingStatusRead,
)
def get_onboarding_status(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    user = onboarding_status_service.get_user_with_status(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    farm_count = sum(
        1
        for farm in user.farms
    )

    return {
        "status": user.onboarding_status,
        "farm_count": farm_count,
        "needs_setup": user.onboarding_status != "completed",
    }
