from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.farm import Farm
from app.models.pond import Pond
from app.models.species import Species
from app.models.user import User
from app.schemas.onboarding import OnboardingSetupCreate


def create_onboarding_setup(
    db: Session,
    owner_id: UUID,
    data: OnboardingSetupCreate,
) -> Farm:

    user = db.get(User, owner_id)

    if user is None:
        raise ValueError("User not found.")

    existing_farm = db.scalar(
        select(Farm).where(
            Farm.owner_id == owner_id,
            Farm.name == data.farm.name,
        )
    )

    if existing_farm is not None:
        raise ValueError(
            "A farm with this name already exists."
        )

    species_ids = {
        pond.species_id
        for pond in data.ponds
    }

    species_rows = list(
        db.scalars(
            select(Species).where(
                Species.id.in_(species_ids),
                Species.is_active.is_(True),
            )
        ).all()
    )

    valid_species_ids = {
        species.id
        for species in species_rows
    }

    invalid_species = species_ids - valid_species_ids

    if invalid_species:
        raise ValueError(
            "One or more selected species do not exist or are inactive."
        )

    farm = Farm(
        owner_id=owner_id,
        **data.farm.model_dump(),
    )

    db.add(farm)
    db.flush()

    for pond_data in data.ponds:
        pond = Pond(
            farm_id=farm.id,
            **pond_data.model_dump(),
        )

        db.add(pond)

    user.onboarding_status = "completed"

    db.commit()

    statement = (
        select(Farm)
        .options(
            joinedload(Farm.ponds)
            .joinedload(Pond.species)
        )
        .where(Farm.id == farm.id)
    )

    return db.execute(statement).unique().scalar_one()
