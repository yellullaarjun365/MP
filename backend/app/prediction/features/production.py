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
    FeatureDefinition(
        "pond_area_m2",
        "float",
        True,
    ),
    FeatureDefinition(
        "pond_depth_m",
        "float",
        False,
    ),
    FeatureDefinition(
        "stocking_count",
        "float",
        True,
    ),
    FeatureDefinition(
        "stocking_density_per_m2",
        "float",
        True,
    ),
    FeatureDefinition(
        "survival_rate",
        "float",
        True,
    ),    FeatureDefinition(
        "growth_rate_g_week",
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
    FeatureDefinition(
        "ph",
        "float",
        False,
    ),
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

    # --------------------------------------------------------
    # Stocking density.
    # --------------------------------------------------------

    if (
        data.stocking_count is not None
        and data.pond_area_m2 is not None
        and data.pond_area_m2 > 0
    ):

        result[
            "stocking_density_per_m2"
        ] = (
            float(
                data.stocking_count
            )
            /
            float(
                data.pond_area_m2
            )
        )

    # --------------------------------------------------------
    # Initial biomass.
    # --------------------------------------------------------

    if (
        data.stocking_count is not None
        and data.initial_average_weight_g is not None
    ):

        result[
            "initial_biomass_kg"
        ] = (
            float(
                data.stocking_count
            )
            *
            float(
                data.initial_average_weight_g
            )
            /
            1000.0
        )

    # --------------------------------------------------------
    # Density-growth relationship.
    #
    # This matches the synthetic V1.1 generator:
    #
    # reference density = 25 PL/m2
    # maximum penalty   = 0.28
    # operational max   = 150 PL/m2
    #
    # This is an evidence-informed synthetic relationship,
    # not a universal empirically calibrated farm equation.
    # --------------------------------------------------------

    density = result.get(
        "stocking_density_per_m2"
    )

    if density is not None:

        reference_density = 25.0
        operational_max = 150.0
        maximum_penalty = 0.28

        normalized_density = (
            density
            -
            reference_density
        ) / (
            operational_max
            -
            reference_density
        )

        normalized_density = max(
            0.0,
            min(
                normalized_density,
                1.0,
            )
        )

        multiplier = (
            1.0
            -
            maximum_penalty
            *
            normalized_density
        )

        result[
            "density_growth_multiplier"
        ] = float(
            multiplier
        )

        # ----------------------------------------------------
        # Effective growth.
        # ----------------------------------------------------

        if data.growth_rate_g_week is not None:

            result[
                "effective_growth_rate_g_week"
            ] = float(
                data.growth_rate_g_week
                *
                multiplier
            )

    return result

def build_model_features(
    data: ProductionPredictionInput,
) -> dict[str, object]:

    features = build_feature_dict(data)

    derived = calculate_derived_features(data)

    features.update(derived)

    return features
