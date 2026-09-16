from __future__ import annotations

from sqlalchemy.engine import Engine

from app.prediction.features.production import (
    build_model_features,
)
from app.prediction.schemas.production import (
    ProductionPredictionInput,
    ProductionPredictionOutput,
)
from app.prediction.services.readiness import (
    check_prediction_readiness,
)


def predict_production(
    engine: Engine,
    data: ProductionPredictionInput,
) -> ProductionPredictionOutput:

    readiness = check_prediction_readiness(
        engine,
        data,
    )

    if not readiness.ready:
        raise ValueError(
            readiness.message
        )

    # Build features now so this service boundary
    # is ready for the validated ML model.
    build_model_features(data)

    raise RuntimeError(
        "No validated production model is registered."
    )
