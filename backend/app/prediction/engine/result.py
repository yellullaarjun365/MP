from __future__ import annotations

from datetime import datetime, timezone

from typing import Any

from pydantic import BaseModel, Field


class StandardPredictionResult(BaseModel):

    task: str

    model_id: str

    model_version: str | None = None

    prediction: float | dict[str, Any]

    target: str

    target_units: str | None = None

    confidence: float | None = None

    uncertainty: dict[str, Any] | None = None

    real_world_validated: bool = False

    source_type: str = "unknown"

    generated_at: datetime = Field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            )
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
