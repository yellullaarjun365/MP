from pydantic import BaseModel, Field


class AquacultureParameters(BaseModel):
    species: str | None = None

    pond_area: float | None = Field(
        default=None,
        ge=0,
    )

    pond_area_unit: str | None = None

    pond_volume_m3: float | None = Field(
        default=None,
        ge=0,
    )

    stocking_count: int | None = Field(
        default=None,
        ge=0,
    )

    average_weight_g: float | None = Field(
        default=None,
        ge=0,
    )

    survival_rate_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    temperature_c: float | None = None

    ph: float | None = Field(
        default=None,
        ge=0,
        le=14,
    )

    dissolved_oxygen_mg_l: float | None = Field(
        default=None,
        ge=0,
    )

    salinity_ppt: float | None = Field(
        default=None,
        ge=0,
    )

    feed_kg_per_day: float | None = Field(
        default=None,
        ge=0,
    )


class ExtractionResult(BaseModel):
    parameters: AquacultureParameters
    missing_fields: list[str] = []
    ambiguities: list[str] = []
