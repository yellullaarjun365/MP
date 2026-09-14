from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.pond import Pond
from app.models.species import Species
from app.models.water_quality import WaterQualityMeasurement
from app.models.feeding import FeedingRecord
from app.models.stocking import StockingRecord
from app.models.growth import GrowthRecord
from app.models.health import HealthEvent
from app.models.harvest import HarvestRecord
from app.schemas.operations import (
    FeedingCreate,
    GrowthCreate,
    HarvestCreate,
    HealthCreate,
    StockingCreate,
    WaterQualityCreate,
)


def owned_pond(
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


def create_water_quality(
    db: Session,
    owner_id: UUID,
    data: WaterQualityCreate,
) -> WaterQualityMeasurement:
    if owned_pond(db, owner_id, data.pond_id) is None:
        raise ValueError("Pond not found.")

    record = WaterQualityMeasurement(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_water_quality(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> list[WaterQualityMeasurement]:
    if owned_pond(db, owner_id, pond_id) is None:
        raise ValueError("Pond not found.")

    statement = (
        select(WaterQualityMeasurement)
        .where(WaterQualityMeasurement.pond_id == pond_id)
        .order_by(WaterQualityMeasurement.measured_at.desc())
    )

    return list(db.scalars(statement).all())


def create_feeding(
    db: Session,
    owner_id: UUID,
    data: FeedingCreate,
) -> FeedingRecord:
    if owned_pond(db, owner_id, data.pond_id) is None:
        raise ValueError("Pond not found.")

    record = FeedingRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_feeding(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> list[FeedingRecord]:
    if owned_pond(db, owner_id, pond_id) is None:
        raise ValueError("Pond not found.")

    statement = (
        select(FeedingRecord)
        .where(FeedingRecord.pond_id == pond_id)
        .order_by(FeedingRecord.fed_at.desc())
    )

    return list(db.scalars(statement).all())


def create_stocking(
    db: Session,
    owner_id: UUID,
    data: StockingCreate,
) -> StockingRecord:
    if owned_pond(db, owner_id, data.pond_id) is None:
        raise ValueError("Pond not found.")

    species = db.get(Species, data.species_id)

    if species is None or not species.is_active:
        raise ValueError("Species not found or inactive.")

    record = StockingRecord(**data.model_dump())

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_stocking(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> list[StockingRecord]:
    if owned_pond(db, owner_id, pond_id) is None:
        raise ValueError("Pond not found.")

    statement = (
        select(StockingRecord)
        .where(StockingRecord.pond_id == pond_id)
        .order_by(StockingRecord.stocked_at.desc())
    )

    return list(db.scalars(statement).all())


def create_growth(
    db: Session,
    owner_id: UUID,
    data: GrowthCreate,
) -> GrowthRecord:
    if owned_pond(db, owner_id, data.pond_id) is None:
        raise ValueError("Pond not found.")

    record = GrowthRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_growth(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> list[GrowthRecord]:
    if owned_pond(db, owner_id, pond_id) is None:
        raise ValueError("Pond not found.")

    statement = (
        select(GrowthRecord)
        .where(GrowthRecord.pond_id == pond_id)
        .order_by(GrowthRecord.sampled_at.desc())
    )

    return list(db.scalars(statement).all())


def create_health(
    db: Session,
    owner_id: UUID,
    data: HealthCreate,
) -> HealthEvent:
    if owned_pond(db, owner_id, data.pond_id) is None:
        raise ValueError("Pond not found.")

    record = HealthEvent(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_health(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> list[HealthEvent]:
    if owned_pond(db, owner_id, pond_id) is None:
        raise ValueError("Pond not found.")

    statement = (
        select(HealthEvent)
        .where(HealthEvent.pond_id == pond_id)
        .order_by(HealthEvent.observed_at.desc())
    )

    return list(db.scalars(statement).all())


def create_harvest(
    db: Session,
    owner_id: UUID,
    data: HarvestCreate,
) -> HarvestRecord:
    if owned_pond(db, owner_id, data.pond_id) is None:
        raise ValueError("Pond not found.")

    record = HarvestRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_harvest(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> list[HarvestRecord]:
    if owned_pond(db, owner_id, pond_id) is None:
        raise ValueError("Pond not found.")

    statement = (
        select(HarvestRecord)
        .where(HarvestRecord.pond_id == pond_id)
        .order_by(HarvestRecord.harvested_at.desc())
    )

    return list(db.scalars(statement).all())
