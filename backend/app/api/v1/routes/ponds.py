from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.pond import PondCreate, PondRead, PondUpdate
from app.services import pond_service


router = APIRouter(
    prefix="/ponds",
    tags=["Ponds"],
)


@router.post(
    "",
    response_model=PondRead,
    status_code=status.HTTP_201_CREATED,
)
def create_pond(
    data: PondCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return pond_service.create_pond(
            db,
            owner_id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/farm/{farm_id}",
    response_model=list[PondRead],
)
def list_ponds(
    farm_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    return pond_service.list_ponds(
        db,
        owner_id,
        farm_id,
    )


@router.get("/{pond_id}", response_model=PondRead)
def get_pond(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    pond = pond_service.get_pond(
        db,
        owner_id,
        pond_id,
    )

    if pond is None:
        raise HTTPException(
            status_code=404,
            detail="Pond not found.",
        )

    return pond


@router.patch("/{pond_id}", response_model=PondRead)
def update_pond(
    pond_id: UUID,
    data: PondUpdate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    pond = pond_service.get_pond(
        db,
        owner_id,
        pond_id,
    )

    if pond is None:
        raise HTTPException(
            status_code=404,
            detail="Pond not found.",
        )

    try:
        return pond_service.update_pond(
            db,
            owner_id,
            pond,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{pond_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pond(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    pond = pond_service.get_pond(
        db,
        owner_id,
        pond_id,
    )

    if pond is None:
        raise HTTPException(
            status_code=404,
            detail="Pond not found.",
        )

    pond_service.delete_pond(db, pond)
