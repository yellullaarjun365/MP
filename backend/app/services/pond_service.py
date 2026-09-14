from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.pond import Pond
from app.models.species import Species
from app.schemas.pond import PondCreate, PondUpdate


def create_pond(
    db: Session,
    owner_id: UUID,
    data: PondCreate,
) -> Pond:
    farm = db.scalar(
        select(Farm).where(
            Farm.id == data.farm_id,
            Farm.owner_id == owner_id,
        )
    )

    if farm is None:
        raise ValueError("Farm not found or not owned by this user.")

    if data.species_id is not None:
        species = db.get(Species, data.species_id)

        if species is None or not species.is_active:
            raise ValueError("Species not found or inactive.")

    pond_data = data.model_dump()

    pond = Pond(**pond_data)

    db.add(pond)
    db.commit()
    db.refresh(pond)

    return pond


def list_ponds(
    db: Session,
    owner_id: UUID,
    farm_id: UUID,
) -> list[Pond]:
    statement = (
        select(Pond)
        .join(Farm, Pond.farm_id == Farm.id)
        .where(
            Pond.farm_id == farm_id,
            Farm.owner_id == owner_id,
        )
        .order_by(Pond.name)
    )

    return list(db.scalars(statement).all())


def get_pond(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> Pond | None:
    statement = (
        select(Pond)
        .join(Farm, Pond.farm_id == Farm.id)
        .where(
            Pond.id == pond_id,
            Farm.owner_id == owner_id,
        )
    )

    return db.scalar(statement)


def update_pond(
    db: Session,
    owner_id: UUID,
    pond: Pond,
    data: PondUpdate,
) -> Pond:
    changes = data.model_dump(exclude_unset=True)

    if "species_id" in changes and changes["species_id"] is not None:
        species = db.get(Species, changes["species_id"])

        if species is None or not species.is_active:
            raise ValueError("Species not found or inactive.")

    for field, value in changes.items():
        setattr(pond, field, value)

    db.commit()
    db.refresh(pond)

    return pond


def delete_pond(
    db: Session,
    pond: Pond,
) -> None:
    db.delete(pond)
    db.commit()
