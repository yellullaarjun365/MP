from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.data_registry.service import (
    load_datasets,
    load_models,
    load_sources,
    load_licenses,
    registry_summary,
)


router = APIRouter(
    prefix="/registry",
    tags=["intelligence-registry"],
)


@router.get(
    "/summary",
)
def get_registry_summary() -> dict[str, Any]:

    try:

        return registry_summary()

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=503,
            detail=f"Registry unavailable: {exc}",
        ) from exc


@router.get(
    "/datasets",
)
def get_datasets() -> dict[str, Any]:

    try:

        items = load_datasets()

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=503,
            detail=f"Dataset registry unavailable: {exc}",
        ) from exc

    return {
        "resource_type": "dataset",
        "count": len(items),
        "items": items,
    }


@router.get(
    "/models",
)
def get_models() -> dict[str, Any]:

    try:

        items = load_models()

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=503,
            detail=f"Model registry unavailable: {exc}",
        ) from exc

    return {
        "resource_type": "model",
        "count": len(items),
        "items": items,
    }


@router.get(
    "/sources",
)
def get_sources() -> dict[str, Any]:

    try:

        items = load_sources()

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=503,
            detail=f"Source registry unavailable: {exc}",
        ) from exc

    return {
        "resource_type": "source",
        "count": len(items),
        "items": items,
    }


@router.get(
    "/licenses",
)
def get_licenses() -> dict[str, Any]:

    try:

        items = load_licenses()

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=503,
            detail=f"License registry unavailable: {exc}",
        ) from exc

    return {
        "resource_type": "license",
        "count": len(items),
        "items": items,
    }
