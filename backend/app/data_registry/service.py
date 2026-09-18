from __future__ import annotations

from pathlib import Path
from typing import Any

import json


BACKEND_ROOT = (
    Path(__file__).resolve().parents[2]
)

REGISTRY_ROOT = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "registry"
)


def _read_json(
    filename: str,
) -> dict[str, Any]:

    path = (
        REGISTRY_ROOT
        / filename
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Registry file not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


def load_datasets() -> list[dict[str, Any]]:

    return _read_json(
        "datasets.json"
    )[
        "datasets"
    ]


def load_models() -> list[dict[str, Any]]:

    return _read_json(
        "models.json"
    )[
        "models"
    ]


def load_sources() -> list[dict[str, Any]]:

    return _read_json(
        "sources.json"
    )[
        "sources"
    ]


def load_licenses() -> list[dict[str, Any]]:

    return _read_json(
        "licenses.json"
    )[
        "licenses"
    ]


def registry_summary() -> dict[str, Any]:

    datasets = load_datasets()
    models = load_models()

    return {
        "dataset_count":
            len(datasets),

        "model_count":
            len(models),

        "training_approved_models":
            len(
                [
                    item
                    for item in models
                    if item.get(
                        "training_approved"
                    )
                ]
            ),

        "real_world_validated_models":
            len(
                [
                    item
                    for item in models
                    if item.get(
                        "real_world_validated"
                    )
                ]
            ),

        "deployment_approved_models":
            len(
                [
                    item
                    for item in models
                    if item.get(
                        "production_deployment_approved"
                    )
                ]
            ),

        "real_world_datasets":
            len(
                [
                    item
                    for item in datasets
                    if item.get(
                        "dataset_type"
                    )
                    ==
                    "real_world_observational"
                ]
            ),

        "synthetic_datasets":
            len(
                [
                    item
                    for item in datasets
                    if (
                        "synthetic"
                        in str(
                            item.get(
                                "dataset_type",
                                ""
                            )
                        ).lower()
                    )
                ]
            ),
    }
