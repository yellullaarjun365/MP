from __future__ import annotations

from dataclasses import dataclass

from app.prediction.schemas.production import (
    ProductionPredictionInput,
)


FEATURE_SCHEMA_VERSION = "production-features-v1"


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    dtype: str
    required: bool


FEATURES = [
    FeatureDefinition("pond_area_m2", "float", True),
    FeatureDefinition("pond_depth_m", "float", False),
    FeatureDefinition("stocking_count", "float", True),
    FeatureDefinition(
        "stocking_density_per_m2",
        "float",
        True,
    ),
    FeatureDefinition(
        "initial_average_weight_g",
        "float",
        False,
    ),
    FeatureDefinition(
        "initial_biomass_kg",
        "float",
        False,
    ),
    FeatureDefinition(
        "temperature_c",
        "float",
        False,
    ),
    FeatureDefinition("ph", "float", False),
    FeatureDefinition(
        "dissolved_oxygen_mg_l",
        "float",
        False,
    ),
    FeatureDefinition(
        "ammonia_mg_l",
        "float",
        False,
    ),
    FeatureDefinition(
        "nitrite_mg_l",
        "float",
        False,
    ),
    FeatureDefinition(
        "salinity_ppt",
        "float",
        False,
    ),
    FeatureDefinition(
        "feed_kg_day",
        "float",
        False,
    ),
    FeatureDefinition(
        "feed_frequency",
        "float",
        False,
    ),
    FeatureDefinition(
        "water_exchange_rate",
        "float",
        False,
    ),
    FeatureDefinition(
        "culture_days",
        "float",
        True,
    ),
    FeatureDefinition(
        "mortality_rate",
        "float",
        False,
    ),
]


def build_feature_dict(
    data: ProductionPredictionInput,
) -> dict[str, object]:

    values = data.model_dump()

    return {
        feature.name: values.get(
            feature.name
        )
        for feature in FEATURES
    }


def calculate_derived_features(
    data: ProductionPredictionInput,
) -> dict[str, float]:

    result: dict[str, float] = {}

    if (
        data.stocking_count is not None
        and data.pond_area_m2 is not None
        and data.pond_area_m2 > 0
    ):
        result["stocking_density_per_m2"] = (
            data.stocking_count
            / data.pond_area_m2
        )

    if (
        data.stocking_count is not None
        and data.initial_average_weight_g is not None
    ):
        result["initial_biomass_kg"] = (
            data.stocking_count
            * data.initial_average_weight_g
            / 1000.0
        )

    return result


def build_model_features(
    data: ProductionPredictionInput,
) -> dict[str, object]:

    features = build_feature_dict(data)

    derived = calculate_derived_features(data)

    features.update(derived)

    return features
