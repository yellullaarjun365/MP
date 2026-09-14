from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmUpdate


def create_farm(
    db: Session,
    owner_id: UUID,
    data: FarmCreate,
) -> Farm:
    user = db.get(User, owner_id)

    if user is None:
        raise ValueError("User not found.")

    farm = Farm(
        owner_id=owner_id,
        **data.model_dump(),
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farm


def list_farms(
    db: Session,
    owner_id: UUID,
) -> list[Farm]:
    statement = (
        select(Farm)
        .where(Farm.owner_id == owner_id)
        .order_by(Farm.name)
    )

    return list(db.scalars(statement).all())


def get_farm(
    db: Session,
    owner_id: UUID,
    farm_id: UUID,
) -> Farm | None:
    statement = (
        select(Farm)
        .where(
            Farm.id == farm_id,
            Farm.owner_id == owner_id,
        )
    )

    return db.scalar(statement)


def update_farm(
    db: Session,
    farm: Farm,
    data: FarmUpdate,
) -> Farm:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(farm, field, value)

    db.commit()
    db.refresh(farm)

    return farm


def delete_farm(
    db: Session,
    farm: Farm,
) -> None:
    db.delete(farm)
    db.commit()
