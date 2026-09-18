from __future__ import annotations

from datetime import datetime, timezone

from app.prediction.features.production import (
    build_model_features,
)

from app.prediction.models.catboost import (
    MODEL_FEATURES,
    predict,
)

from app.prediction.schemas.production import (
    ProductionPredictionInput,
    ProductionPredictionOutput,
)


MODEL_NAME = "CatBoostRegressor"

MODEL_VERSION = (
    "production-catboost-v0.2"
)

FEATURE_SCHEMA_VERSION = (
    "prediction-input-v1"
)


def run_production_prediction(
    request: ProductionPredictionInput,
) -> ProductionPredictionOutput:

    # --------------------------------------------------------
    # Build inference features from the canonical feature
    # builder.
    # --------------------------------------------------------

    features = build_model_features(
        request
    )

    missing = [
        name
        for name in MODEL_FEATURES
        if name not in features
        or features[name] is None
    ]

    if missing:

        raise ValueError(
            "Missing model features: "
            +
            ", ".join(missing)
        )

    # --------------------------------------------------------
    # Predict.
    # --------------------------------------------------------

    prediction_kg = predict(
        features
    )

    # --------------------------------------------------------
    # Build the ACTUAL response contract.
    #
    # ProductionPredictionOutput uses:
    #
    #   predicted_production_kg
    #
    # NOT:
    #
    #   prediction_kg
    # --------------------------------------------------------

    return ProductionPredictionOutput(
        target="production_kg",

        predicted_production_kg=float(
            prediction_kg
        ),

        uncertainty=None,

        confidence=None,

        model_name=MODEL_NAME,

        model_version=MODEL_VERSION,

        feature_schema_version=(
            FEATURE_SCHEMA_VERSION
        ),

        generated_at=datetime.now(
            timezone.utc
        ),
    )
