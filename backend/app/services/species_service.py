from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.species import Species
from app.schemas.species import SpeciesCreate, SpeciesUpdate


def list_species(
    db: Session,
    active_only: bool = True,
) -> list[Species]:
    statement = select(Species).order_by(Species.common_name)

    if active_only:
        statement = statement.where(Species.is_active.is_(True))

    return list(db.scalars(statement).all())


def get_species(
    db: Session,
    species_id: UUID,
) -> Species | None:
    return db.get(Species, species_id)


def create_species(
    db: Session,
    data: SpeciesCreate,
) -> Species:
    existing = db.scalar(
        select(Species).where(
            Species.common_name == data.common_name
        )
    )

    if existing is not None:
        raise ValueError("A species with this common name already exists.")

    species = Species(
        common_name=data.common_name,
        scientific_name=data.scientific_name,
        category=data.category,
        is_active=True,
    )

    db.add(species)
    db.commit()
    db.refresh(species)

    return species


def update_species(
    db: Session,
    species: Species,
    data: SpeciesUpdate,
) -> Species:
    changes = data.model_dump(exclude_unset=True)

    if "common_name" in changes:
        existing = db.scalar(
            select(Species).where(
                Species.common_name == changes["common_name"],
                Species.id != species.id,
            )
        )

        if existing is not None:
            raise ValueError(
                "A species with this common name already exists."
            )

    for field, value in changes.items():
        setattr(species, field, value)

    db.commit()
    db.refresh(species)

    return species
