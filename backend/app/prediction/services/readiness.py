from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.prediction.schemas.production import (
    PredictionReadiness,
    ProductionPredictionInput,
)


REQUIRED_INPUT_FIELDS = [
    "pond_area_m2",
    "stocking_count",
    "culture_days",
]


HISTORICAL_TABLES = {
    "stocking_records",
    "growth_records",
    "water_quality_measurements",
    "feeding_records",
    "health_events",
    "harvest_records",
}


def count_historical_records(
    engine: Engine,
) -> int:

    total = 0

    with engine.connect() as connection:

        for table in HISTORICAL_TABLES:

            result = connection.execute(
                text(
                    f'SELECT COUNT(*) FROM "{table}"'
                )
            )

            total += int(
                result.scalar() or 0
            )

    return total


def check_prediction_readiness(
    engine: Engine,
    data: ProductionPredictionInput | None = None,
) -> PredictionReadiness:

    values = (
        data.model_dump()
        if data is not None
        else {}
    )

    missing: list[str] = []

    for field in REQUIRED_INPUT_FIELDS:

        value = values.get(field)

        if value is None:
            missing.append(field)

    available = [
        key
        for key, value in values.items()
        if value is not None
    ]

    historical = count_historical_records(
        engine
    )

    if historical == 0:

        ready = False

        message = (
            "No historical production data "
            "is available. A validated production "
            "model cannot be enabled yet."
        )

    elif missing:

        ready = False

        message = (
            "Prediction request is missing "
            "required farm fields."
        )

    else:

        ready = False

        message = (
            "Input structure is valid, but "
            "no validated production model "
            "is registered."
        )

    return PredictionReadiness(
        ready=ready,
        required_fields=REQUIRED_INPUT_FIELDS,
        missing_fields=missing,
        available_fields=available,
        historical_records=historical,
        message=message,
    )
