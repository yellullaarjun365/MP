from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.farm import FarmCreate, FarmRead, FarmUpdate
from app.services import farm_service


router = APIRouter(
    prefix="/farms",
    tags=["Farms"],
)


@router.post(
    "",
    response_model=FarmRead,
    status_code=status.HTTP_201_CREATED,
)
def create_farm(
    data: FarmCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return farm_service.create_farm(
            db,
            owner_id,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[FarmRead])
def list_farms(
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    return farm_service.list_farms(db, owner_id)


@router.get("/{farm_id}", response_model=FarmRead)
def get_farm(
    farm_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    farm = farm_service.get_farm(
        db,
        owner_id,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found.",
        )

    return farm


@router.patch("/{farm_id}", response_model=FarmRead)
def update_farm(
    farm_id: UUID,
    data: FarmUpdate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    farm = farm_service.get_farm(
        db,
        owner_id,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found.",
        )

    return farm_service.update_farm(
        db,
        farm,
        data,
    )


@router.delete(
    "/{farm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_farm(
    farm_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    farm = farm_service.get_farm(
        db,
        owner_id,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found.",
        )

    farm_service.delete_farm(db, farm)
