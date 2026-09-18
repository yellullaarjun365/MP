from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from catboost import CatBoostRegressor


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "production-catboost-v0.2.cbm"
)


MODEL_FEATURES = [
    "pond_area_m2",
    "pond_depth_m",
    "stocking_density_per_m2",
    "stocking_count",
    "initial_average_weight_g",
    "initial_biomass_kg",
    "culture_days",
    "survival_rate",
    "growth_rate_g_week",
    "density_growth_multiplier",
    "effective_growth_rate_g_week",
]


@lru_cache(maxsize=1)
def load_model() -> CatBoostRegressor:

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model artifact not found: {MODEL_PATH}"
        )

    model = CatBoostRegressor()

    model.load_model(
        MODEL_PATH
    )

    return model


def predict(
    features: dict[str, float],
) -> float:

    model = load_model()

    missing = [
        name
        for name in MODEL_FEATURES
        if name not in features
    ]

    if missing:

        raise ValueError(
            "Missing model features: "
            +
            ", ".join(missing)
        )

    ordered = [
        features[name]
        for name in MODEL_FEATURES
    ]

    prediction = model.predict(
        [ordered]
    )[0]

    return max(
        float(prediction),
        0.0,
    )
