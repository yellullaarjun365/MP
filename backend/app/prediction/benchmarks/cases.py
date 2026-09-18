
from __future__ import annotations

from pydantic import BaseModel, Field


class BenchmarkCase(BaseModel):

    benchmark_id: str

    task: str

    target: str

    target_units: str | None = None

    dataset_id: str

    dataset_type: str

    real_world: bool

    synthetic: bool

    aggregated: bool

    leakage_protected: bool

    execution_required: bool = False

    notes: list[str] = Field(
        default_factory=list
    )


class BenchmarkResult(BaseModel):

    benchmark_id: str

    model_id: str

    status: str

    metrics: dict = Field(
        default_factory=dict
    )

    observations: int = 0

    dataset_id: str

    execution_status: str = (
        "NOT_EXECUTED"
    )

    real_world_validated: bool = False

    production_approved: bool = False

    notes: list[str] = Field(
        default_factory=list
    )
