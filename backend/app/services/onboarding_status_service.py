from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.user import User


def refresh_onboarding_status(
    db: Session,
    user: User,
) -> User:
    farm_count = db.scalar(
        select(func.count(Farm.id))
        .where(Farm.owner_id == user.id)
    ) or 0

    if farm_count == 0:
        user.onboarding_status = "not_started"
    else:
        user.onboarding_status = "completed"

    db.commit()
    db.refresh(user)

    return user


def get_user_with_status(
    db: Session,
    user_id: UUID,
) -> User | None:
    user = db.get(User, user_id)

    if user is None:
        return None

    return refresh_onboarding_status(db, user)
