from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.farm import Farm
from app.models.user import User


def get_current_user(
    db: Session,
    user_id: UUID,
) -> User | None:
    statement = (
        select(User)
        .options(
            selectinload(User.farms)
        )
        .where(User.id == user_id)
    )

    return db.scalar(statement)


def get_farm_count(
    db: Session,
    user_id: UUID,
) -> int:
    statement = select(Farm.id).where(
        Farm.owner_id == user_id
    )

    return len(db.scalars(statement).all())
