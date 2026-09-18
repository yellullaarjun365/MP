
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExternalAdapterSpec(BaseModel):

    adapter_id: str

    model_id: str

    source_id: str

    source_url: str

    task: str

    framework: list[str] = Field(
        default_factory=list
    )

    candidate_features: list[str] = Field(
        default_factory=list
    )

    license: str

    license_verified: bool

    artifact_available: bool

    artifact_count: int

    repository_available: bool

    archive_sha256: str | None = None

    execution_allowed: bool = False

    weights_loaded: bool = False

    benchmark_allowed: bool = False

    approval_status: str = (
        "NOT_APPROVED"
    )

    notes: list[str] = Field(
        default_factory=list
    )
