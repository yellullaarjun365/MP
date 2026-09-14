from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.me import MeRead
from app.services import user_service


router = APIRouter(
    prefix="/me",
    tags=["User"],
)


@router.get(
    "",
    response_model=MeRead,
)
def get_me(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    user = user_service.get_current_user(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "onboarding_status": user.onboarding_status,
        "farms": user.farms,
        "farm_count": len(user.farms),
    }
