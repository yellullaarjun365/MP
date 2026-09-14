from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.species import (
    SpeciesCreate,
    SpeciesRead,
    SpeciesUpdate,
)
from app.services import species_service


router = APIRouter(
    prefix="/species",
    tags=["Species"],
)


@router.get(
    "",
    response_model=list[SpeciesRead],
)
def list_species(
    db: Session = Depends(get_db),
    _user_id: UUID = Depends(get_current_user_id),
):
    return species_service.list_species(db)


@router.get(
    "/{species_id}",
    response_model=SpeciesRead,
)
def get_species(
    species_id: UUID,
    db: Session = Depends(get_db),
    _user_id: UUID = Depends(get_current_user_id),
):
    species = species_service.get_species(
        db,
        species_id,
    )

    if species is None:
        raise HTTPException(
            status_code=404,
            detail="Species not found.",
        )

    return species


@router.post(
    "",
    response_model=SpeciesRead,
    status_code=status.HTTP_201_CREATED,
)
def create_species(
    data: SpeciesCreate,
    db: Session = Depends(get_db),
    _user_id: UUID = Depends(get_current_user_id),
):
    try:
        return species_service.create_species(
            db,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{species_id}",
    response_model=SpeciesRead,
)
def update_species(
    species_id: UUID,
    data: SpeciesUpdate,
    db: Session = Depends(get_db),
    _user_id: UUID = Depends(get_current_user_id),
):
    species = species_service.get_species(
        db,
        species_id,
    )

    if species is None:
        raise HTTPException(
            status_code=404,
            detail="Species not found.",
        )

    try:
        return species_service.update_species(
            db,
            species,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
