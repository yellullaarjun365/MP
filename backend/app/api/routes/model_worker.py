
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.model_worker.schemas.manifest import (
    WorkerRequest,
)

from app.model_worker.service import (
    run_worker_request,
)


router = APIRouter(
    prefix="/model-worker",
    tags=[
        "model-worker"
    ],
)


@router.post(
    "/prepare"
)
def prepare_worker(
    request: WorkerRequest,
):

    try:

        result = run_worker_request(
            request
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


    return result.model_dump()
