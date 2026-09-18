from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class RegistryResource(BaseModel):
    resource_type: Literal[
        "dataset",
        "model",
        "source",
        "license",
    ]

    resource_id: str
    name: str
    status: str | None = None
    source: str | None = None


class RegistrySummary(BaseModel):
    dataset_count: int
    model_count: int
    training_approved_models: int
    real_world_validated_models: int
    deployment_approved_models: int
    real_world_datasets: int
    synthetic_datasets: int
