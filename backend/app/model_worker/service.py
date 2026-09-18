
from __future__ import annotations

from app.model_worker.runtime.executor import (
    execute_request,
)

from app.model_worker.schemas.manifest import (
    WorkerRequest,
    WorkerResult,
)


def run_worker_request(
    request: WorkerRequest,
) -> WorkerResult:

    return execute_request(
        request
    )
