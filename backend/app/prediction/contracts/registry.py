from __future__ import annotations

from app.prediction.contracts.tasks import (
    FeatureContract,
    FeatureSpec,
    PredictionTask,
)


POND_PRODUCTION_CONTRACT = FeatureContract(
    contract_id="aqualife-pond-production-v1",
    task=PredictionTask.POND_PRODUCTION,
    features=[
        FeatureSpec(
            name="pond_area_m2",
            dtype="float",
            required=True,
            units="m2",
        ),
        FeatureSpec(
            name="pond_depth_m",
            dtype="float",
            required=False,
            units="m",
        ),
        FeatureSpec(
            name="stocking_density_per_m2",
            dtype="float",
            required=True,
            units="fish/m2",
        ),
        FeatureSpec(
            name="stocking_count",
            dtype="float",
            required=True,
            units="fish",
        ),
        FeatureSpec(
            name="initial_average_weight_g",
            dtype="float",
            required=False,
            units="g",
        ),
        FeatureSpec(
            name="initial_biomass_kg",
            dtype="float",
            required=False,
            units="kg",
        ),
        FeatureSpec(
            name="culture_days",
            dtype="float",
            required=True,
            units="days",
        ),
        FeatureSpec(
            name="survival_rate",
            dtype="float",
            required=True,
        ),
        FeatureSpec(
            name="growth_rate_g_week",
            dtype="float",
            required=True,
            units="g/week",
        ),
        FeatureSpec(
            name="density_growth_multiplier",
            dtype="float",
            required=True,
        ),
        FeatureSpec(
            name="effective_growth_rate_g_week",
            dtype="float",
            required=True,
            units="g/week",
        ),
    ],
    target="production_kg",
    target_units="kg",
    granularity="pond",
)


WATER_QUALITY_CONTRACT = FeatureContract(
    contract_id="aqualife-water-quality-v1",
    task=PredictionTask.WATER_QUALITY_FORECAST,
    features=[
        FeatureSpec(
            name="temperature_c",
            dtype="float",
            required=True,
            units="C",
            temporal=True,
        ),
        FeatureSpec(
            name="ph",
            dtype="float",
            required=True,
            temporal=True,
        ),
        FeatureSpec(
            name="dissolved_oxygen_mg_l",
            dtype="float",
            required=True,
            units="mg/L",
            temporal=True,
        ),
        FeatureSpec(
            name="ammonia_mg_l",
            dtype="float",
            required=False,
            units="mg/L",
            temporal=True,
        ),
        FeatureSpec(
            name="nitrite_mg_l",
            dtype="float",
            required=False,
            units="mg/L",
            temporal=True,
        ),
    ],
    target="water_quality",
    temporal_resolution="time_series",
    granularity="pond",
)


DISSOLVED_OXYGEN_CONTRACT = FeatureContract(
    contract_id="aqualife-do-forecast-v1",
    task=PredictionTask.DISSOLVED_OXYGEN_FORECAST,
    features=[
        FeatureSpec(
            name="temperature_c",
            dtype="float",
            required=True,
            units="C",
            temporal=True,
        ),
        FeatureSpec(
            name="ph",
            dtype="float",
            required=False,
            temporal=True,
        ),
        FeatureSpec(
            name="dissolved_oxygen_mg_l",
            dtype="float",
            required=True,
            units="mg/L",
            temporal=True,
        ),
        FeatureSpec(
            name="ammonia_mg_l",
            dtype="float",
            required=False,
            units="mg/L",
            temporal=True,
        ),
        FeatureSpec(
            name="nitrite_mg_l",
            dtype="float",
            required=False,
            units="mg/L",
            temporal=True,
        ),
    ],
    target="dissolved_oxygen_mg_l",
    target_units="mg/L",
    temporal_resolution="time_series",
    granularity="pond",
)


GROWTH_CONTRACT = FeatureContract(
    contract_id="aqualife-growth-v1",
    task=PredictionTask.GROWTH_FORECAST,
    features=[
        FeatureSpec(
            name="culture_days",
            dtype="float",
            required=True,
            units="days",
            temporal=True,
        ),
        FeatureSpec(
            name="initial_average_weight_g",
            dtype="float",
            required=True,
            units="g",
        ),
        FeatureSpec(
            name="feed_kg_day",
            dtype="float",
            required=False,
            units="kg/day",
            temporal=True,
        ),
        FeatureSpec(
            name="temperature_c",
            dtype="float",
            required=False,
            units="C",
            temporal=True,
        ),
        FeatureSpec(
            name="dissolved_oxygen_mg_l",
            dtype="float",
            required=False,
            units="mg/L",
            temporal=True,
        ),
    ],
    target="growth_rate_g_week",
    target_units="g/week",
    temporal_resolution="time_series",
    granularity="pond",
)


BIOMASS_CONTRACT = FeatureContract(
    contract_id="aqualife-biomass-v1",
    task=PredictionTask.BIOMASS_ESTIMATION,
    features=[
        FeatureSpec(
            name="image",
            dtype="image",
            required=True,
        ),
        FeatureSpec(
            name="species",
            dtype="string",
            required=False,
        ),
        FeatureSpec(
            name="pond_id",
            dtype="string",
            required=False,
        ),
    ],
    target="fish_mass",
    target_units="g",
    granularity="fish_or_batch",
)


DISEASE_CONTRACT = FeatureContract(
    contract_id="aqualife-disease-v1",
    task=PredictionTask.DISEASE_DETECTION,
    features=[
        FeatureSpec(
            name="image",
            dtype="image",
            required=True,
        ),
        FeatureSpec(
            name="farmer_description",
            dtype="text",
            required=False,
        ),
        FeatureSpec(
            name="temperature_c",
            dtype="float",
            required=False,
        ),
        FeatureSpec(
            name="dissolved_oxygen_mg_l",
            dtype="float",
            required=False,
        ),
        FeatureSpec(
            name="ph",
            dtype="float",
            required=False,
        ),
    ],
    target="disease_class",
    granularity="fish_or_batch",
)


NITRATE_CONTRACT = FeatureContract(
    contract_id="aqualife-nitrate-v1",
    task=PredictionTask.NITRATE_ESTIMATION,
    features=[
        FeatureSpec(
            name="temperature_c",
            dtype="float",
            required=True,
            units="C",
            temporal=True,
        ),
        FeatureSpec(
            name="ph",
            dtype="float",
            required=True,
            temporal=True,
        ),
        FeatureSpec(
            name="dissolved_oxygen_mg_l",
            dtype="float",
            required=True,
            units="mg/L",
            temporal=True,
        ),
        FeatureSpec(
            name="conductivity",
            dtype="float",
            required=False,
            temporal=True,
        ),
    ],
    target="nitrate_concentration",
    target_units="mg/L",
    temporal_resolution="time_series",
    granularity="pond",
)


CONTRACTS = {
    POND_PRODUCTION_CONTRACT.task.value:
        POND_PRODUCTION_CONTRACT,

    WATER_QUALITY_CONTRACT.task.value:
        WATER_QUALITY_CONTRACT,

    DISSOLVED_OXYGEN_CONTRACT.task.value:
        DISSOLVED_OXYGEN_CONTRACT,

    GROWTH_CONTRACT.task.value:
        GROWTH_CONTRACT,

    BIOMASS_CONTRACT.task.value:
        BIOMASS_CONTRACT,

    DISEASE_CONTRACT.task.value:
        DISEASE_CONTRACT,

    NITRATE_CONTRACT.task.value:
        NITRATE_CONTRACT,
}


def get_contract(
    task: str,
) -> FeatureContract:

    try:

        return CONTRACTS[
            task
        ]

    except KeyError as exc:

        raise ValueError(
            f"Unknown prediction task: {task}"
        ) from exc
