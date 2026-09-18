from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


PredictionTarget = Literal["production_kg"]


class ProductionPredictionInput(BaseModel):
    species: str | None = None

    pond_area_m2: float | None = Field(
        default=None,
        ge=0,
    )

    pond_depth_m: float | None = Field(
        default=None,
        ge=0,
    )

    stocking_count: float | None = Field(
        default=None,
        ge=0,
    )

    stocking_density_per_m2: float | None = Field(
        default=None,
        ge=0,
    )

    initial_average_weight_g: float | None = Field(
        default=None,
        ge=0,
    )

    initial_biomass_kg: float | None = Field(
        default=None,
        ge=0,
    )

    temperature_c: float | None = None

    ph: float | None = None

    dissolved_oxygen_mg_l: float | None = Field(
        default=None,
        ge=0,
    )

    ammonia_mg_l: float | None = Field(
        default=None,
        ge=0,
    )

    nitrite_mg_l: float | None = Field(
        default=None,
        ge=0,
    )

    salinity_ppt: float | None = Field(
        default=None,
        ge=0,
    )

    feed_kg_day: float | None = Field(
        default=None,
        ge=0,
    )

    feed_frequency: float | None = Field(
        default=None,
        ge=0,
    )

    water_exchange_rate: float | None = Field(
        default=None,
        ge=0,
    )

    culture_days: float | None = Field(
        default=None,
        ge=0,
    )
    survival_rate: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    growth_rate_g_week: float | None = Field(
        default=None,
        ge=0,
        le=3,
    )

    mortality_rate: float | None = Field(
        default=None,
        ge=0,
    )


class PredictionRange(BaseModel):
    lower_kg: float
    upper_kg: float


class ProductionPredictionOutput(BaseModel):
    target: PredictionTarget = "production_kg"

    predicted_production_kg: float | None = None

    uncertainty: PredictionRange | None = None

    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    model_name: str | None = None
    model_version: str | None = None

    feature_schema_version: str = "prediction-input-v1"

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PredictionReadiness(BaseModel):
    ready: bool

    required_fields: list[str]

    missing_fields: list[str]

    available_fields: list[str]

    historical_records: int

    message: str
