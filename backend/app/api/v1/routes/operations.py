from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.schemas.operations import (
    FeedingCreate,
    FeedingRead,
    GrowthCreate,
    GrowthRead,
    HarvestCreate,
    HarvestRead,
    HealthCreate,
    HealthRead,
    StockingCreate,
    StockingRead,
    WaterQualityCreate,
    WaterQualityRead,
)
from app.services import operations_service


router = APIRouter(
    prefix="/operations",
    tags=["Operations"],
)


@router.post(
    "/water-quality",
    response_model=WaterQualityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_water_quality(
    data: WaterQualityCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.create_water_quality(
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
    "/water-quality/{pond_id}",
    response_model=list[WaterQualityRead],
)
def list_water_quality(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.list_water_quality(
            db,
            owner_id,
            pond_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/feeding",
    response_model=FeedingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_feeding(
    data: FeedingCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.create_feeding(
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
    "/feeding/{pond_id}",
    response_model=list[FeedingRead],
)
def list_feeding(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.list_feeding(
            db,
            owner_id,
            pond_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/stocking",
    response_model=StockingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_stocking(
    data: StockingCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.create_stocking(
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
    "/stocking/{pond_id}",
    response_model=list[StockingRead],
)
def list_stocking(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.list_stocking(
            db,
            owner_id,
            pond_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/growth",
    response_model=GrowthRead,
    status_code=status.HTTP_201_CREATED,
)
def create_growth(
    data: GrowthCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.create_growth(
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
    "/growth/{pond_id}",
    response_model=list[GrowthRead],
)
def list_growth(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.list_growth(
            db,
            owner_id,
            pond_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/health",
    response_model=HealthRead,
    status_code=status.HTTP_201_CREATED,
)
def create_health(
    data: HealthCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.create_health(
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
    "/health/{pond_id}",
    response_model=list[HealthRead],
)
def list_health(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.list_health(
            db,
            owner_id,
            pond_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/harvest",
    response_model=HarvestRead,
    status_code=status.HTTP_201_CREATED,
)
def create_harvest(
    data: HarvestCreate,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.create_harvest(
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
    "/harvest/{pond_id}",
    response_model=list[HarvestRead],
)
def list_harvest(
    pond_id: UUID,
    db: Session = Depends(get_db),
    owner_id: UUID = Depends(get_current_user_id),
):
    try:
        return operations_service.list_harvest(
            db,
            owner_id,
            pond_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
