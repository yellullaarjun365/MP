from __future__ import annotations

import json

from pathlib import Path

from typing import Any

from app.prediction.engine.compatibility import (
    check_compatibility,
)


BACKEND_ROOT = Path(
    __file__
).resolve().parents[3]


REGISTRY_PATH = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "registry"
    / "models.json"
)


def load_models() -> list[dict[str, Any]]:

    payload = json.loads(
        REGISTRY_PATH.read_text(
            encoding="utf-8-sig"
        )
    )

    return payload.get(
        "models",
        []
    )


def find_models_for_task(
    task: str,
    input_features: dict[str, Any],
):

    candidates = []


    for model in load_models():

        if (
            model.get(
                "task"
            )
            !=
            task
        ):

            continue


        result = check_compatibility(
            task=task,

            model_id=model.get(
                "model_id",
                "unknown",
            ),

            input_features=input_features,

            model_features=model.get(
                "input_features"
            ),
        )


        candidates.append(
            result
        )


    return candidates


def select_development_model(
    task: str,
    input_features: dict[str, Any],
):

    candidates = (
        find_models_for_task(
            task,
            input_features,
        )
    )


    compatible = [
        candidate
        for candidate in candidates
        if candidate.compatible
    ]


    for candidate in compatible:

        if (
            candidate.model_id
            ==
            "aqualife-catboost-production-v0.2"
        ):

            return candidate


    if compatible:

        return compatible[0]


    return None

