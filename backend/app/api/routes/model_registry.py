from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.prediction.engine.selector import (
    find_models_for_task,
)


router = APIRouter(
    prefix="/model-registry",
    tags=["model-registry"],
)


class CompatibilityRequest(BaseModel):

    task: str

    features: dict[str, Any]


@router.post(
    "/compatibility"
)
def check_model_compatibility(
    request: CompatibilityRequest,
) -> dict[str, Any]:

    try:

        candidates = (
            find_models_for_task(
                request.task,
                request.features,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


    return {
        "task": request.task,

        "candidate_count": len(
            candidates
        ),

        "candidates": [
            candidate.model_dump()
            for candidate in candidates
        ],
    }
