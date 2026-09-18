from __future__ import annotations

from typing import Any

from app.prediction.adapters import (
    CatBoostProductionAdapter,
)

from app.prediction.contracts.registry import (
    get_contract,
)

from app.prediction.engine.result import (
    StandardPredictionResult,
)


CATBOOST = (
    CatBoostProductionAdapter()
)


ADAPTERS = {
    CATBOOST.model_id:
        CATBOOST,
}


def predict_with_model(
    model_id: str,
    task: str,
    features: dict[str, Any],
) -> StandardPredictionResult:

    if model_id not in ADAPTERS:

        raise ValueError(
            f"No adapter registered for model: {model_id}"
        )


    adapter = ADAPTERS[
        model_id
    ]


    if adapter.task != task:

        raise ValueError(
            "Model/task mismatch: "
            f"{model_id} != {task}"
        )


    contract = get_contract(
        task
    )


    prediction = adapter.predict(
        features
    )


    return StandardPredictionResult(
        task=task,

        model_id=model_id,

        model_version="0.2",

        prediction=prediction,

        target=contract.target,

        target_units=contract.target_units,

        real_world_validated=False,

        source_type="synthetic",
    )
