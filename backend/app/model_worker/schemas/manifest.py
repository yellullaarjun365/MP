
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApprovedResource(BaseModel):

    resource_id: str

    source_id: str

    source_url: str

    task: str

    artifact_path: str

    artifact_sha256: str

    license: str

    license_verified: bool

    feature_contract: str | None = None

    framework: list[str] = Field(
        default_factory=list
    )

    approved_for_execution: bool = False

    approved_by: str | None = None

    approval_reason: str | None = None

    notes: list[str] = Field(
        default_factory=list
    )


class WorkerRequest(BaseModel):

    resource_id: str

    task: str

    features: dict[str, Any]

    timeout_seconds: int | None = None


class WorkerResult(BaseModel):

    schema_version: str = (
        "aqualife-worker-result-v1"
    )

    resource_id: str

    task: str

    status: str

    execution_status: str

    prediction: Any | None = None

    model_output: dict[str, Any] = Field(
        default_factory=dict
    )

    execution_seconds: float | None = None

    worker_image: str | None = None

    artifact_sha256: str | None = None

    real_world_validated: bool = False

    production_approved: bool = False

    notes: list[str] = Field(
        default_factory=list
    )
