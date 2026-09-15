from typing import Any

from app.schemas.aquaculture_parameters import (
    AquacultureParameters,
)
from app.services.parameter_validation import (
    normalize_parameters,
)


REQUIRED_EXTRACTION_FIELDS = [
    "species",
    "pond_area",
    "pond_area_unit",
    "pond_volume_m3",
    "stocking_count",
    "average_weight_g",
    "survival_rate_percent",
    "temperature_c",
    "ph",
    "dissolved_oxygen_mg_l",
    "salinity_ppt",
    "feed_kg_per_day",
]


def compute_missing_fields(
    parameters: AquacultureParameters,
) -> list[str]:

    data = parameters.model_dump()

    return [
        field
        for field in REQUIRED_EXTRACTION_FIELDS
        if data.get(field) is None
    ]


def normalize_and_validate(
    parameters: AquacultureParameters,
) -> dict[str, Any]:

    normalized = normalize_parameters(
        parameters
    )

    missing = compute_missing_fields(
        normalized
    )

    return {
        "parameters": normalized.model_dump(),
        "missing_fields": missing,
    }


__all__ = [
    "compute_missing_fields",
    "normalize_and_validate",
]
