from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PredictionTask(str, Enum):
    POND_PRODUCTION = "pond_production_regression"
    WATER_QUALITY_FORECAST = "water_quality_forecasting"
    DISSOLVED_OXYGEN_FORECAST = "dissolved_oxygen_forecasting"
    GROWTH_FORECAST = "growth_forecasting"
    BIOMASS_ESTIMATION = "biomass_estimation"
    DISEASE_DETECTION = "disease_detection"
    NITRATE_ESTIMATION = "nitrate_estimation"


class FeatureSpec(BaseModel):

    name: str

    dtype: str

    required: bool = True

    units: str | None = None

    temporal: bool = False


class FeatureContract(BaseModel):

    contract_id: str

    task: PredictionTask

    features: list[FeatureSpec]

    target: str

    target_units: str | None = None

    temporal_resolution: str | None = None

    horizon: str | None = None

    granularity: str = "unknown"


class CompatibilityResult(BaseModel):

    compatible: bool

    task: str

    model_id: str

    missing_features: list[str] = Field(
        default_factory=list
    )

    extra_features: list[str] = Field(
        default_factory=list
    )

    incompatible_features: list[str] = Field(
        default_factory=list
    )

    reasons: list[str] = Field(
        default_factory=list
    )

    score: float = 0.0

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
