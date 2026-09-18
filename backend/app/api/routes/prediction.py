from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.prediction.schemas.production import (
    ProductionPredictionInput,
    ProductionPredictionOutput,
)

from app.prediction.services.inference import (
    run_production_prediction,
)


router = APIRouter(
    prefix="/prediction",
    tags=["prediction"],
)


@router.post(
    "/production",
    response_model=ProductionPredictionOutput,
)
def predict_production(
    request: ProductionPredictionInput,
) -> ProductionPredictionOutput:

    try:

        return run_production_prediction(
            request
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
