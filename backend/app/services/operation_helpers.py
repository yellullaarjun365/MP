from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.pond import Pond


def require_owned_pond(
    db: Session,
    owner_id: UUID,
    pond_id: UUID,
) -> Pond:
    statement = (
        select(Pond)
        .join(Farm, Pond.farm_id == Farm.id)
        .where(
            Pond.id == pond_id,
            Farm.owner_id == owner_id,
        )
    )

    pond = db.scalar(statement)

    if pond is None:
        raise HTTPException(
            status_code=404,
            detail="Pond not found.",
        )

    return pond
