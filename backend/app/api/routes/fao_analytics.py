from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/analytics/fao",
    tags=["fao-analytics"],
)


# ----------------------------------------------------------------
# Canonical data locations
# ----------------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parents[3]

YEARLY_PATH = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "fao"
    / "canonical"
    / "fao-india-vannamei-yearly.csv"
)

ENVIRONMENT_PATH = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "fao"
    / "canonical"
    / "fao-india-vannamei-environment.csv"
)

STATUS_PATH = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "fao"
    / "canonical"
    / "fao-india-vannamei-status.csv"
)

BENCHMARK_REPORT_PATH = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "fao"
    / "reports"
    / "fao-india-vannamei-benchmark-report.json"
)

SOURCE_METADATA_PATH = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "fao"
    / "reports"
    / "fao-source-metadata.json"
)


# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------

def read_csv_rows(
    path: Path,
) -> list[dict[str, str]]:

    if not path.exists():
        raise FileNotFoundError(
            f"Canonical FAO file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        return list(
            csv.DictReader(handle)
        )


def read_json(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():
        raise FileNotFoundError(
            f"FAO report not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


def as_float(
    value: str | None,
) -> float | None:

    if value is None:
        return None

    text = value.strip()

    if not text:
        return None

    return float(text)


def as_int(
    value: str | None,
) -> int | None:

    if value is None:
        return None

    text = value.strip()

    if not text:
        return None

    return int(float(text))


# ----------------------------------------------------------------
# Main endpoint
# ----------------------------------------------------------------

@router.get(
    "/india/vannamei",
)
def get_india_vannamei_history() -> dict[str, Any]:

    try:

        yearly_rows = read_csv_rows(
            YEARLY_PATH
        )

        environment_rows = read_csv_rows(
            ENVIRONMENT_PATH
        )

        status_rows = read_csv_rows(
            STATUS_PATH
        )

        benchmark = read_json(
            BENCHMARK_REPORT_PATH
        )

        source_metadata = read_json(
            SOURCE_METADATA_PATH
        )

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=503,
            detail=f"FAO benchmark unavailable: {exc}",
        ) from exc


    yearly: list[dict[str, Any]] = []

    for row in yearly_rows:

        yearly.append(
            {
                "year":
                    as_int(
                        row.get("year")
                    ),

                "production_tonnes":
                    as_float(
                        row.get(
                            "production_tonnes"
                        )
                    ),

                "production_kg":
                    as_float(
                        row.get(
                            "production_kg"
                        )
                    ),

                "observations":
                    as_int(
                        row.get(
                            "observations"
                        )
                    ),

                "environments":
                    as_int(
                        row.get(
                            "environments"
                        )
                    ),

                "yoy_change_pct":
                    as_float(
                        row.get(
                            "yoy_change_pct"
                        )
                    ),
            }
        )


    environments: list[dict[str, Any]] = []

    for row in environment_rows:

        environments.append(
            {
                "year":
                    as_int(
                        row.get("year")
                    ),

                "environment_code":
                    row.get(
                        "environment_code"
                    ),

                "environment":
                    row.get(
                        "environment"
                    ),

                "production_tonnes":
                    as_float(
                        row.get(
                            "production_tonnes"
                        )
                    ),

                "production_kg":
                    as_float(
                        row.get(
                            "production_kg"
                        )
                    ),

                "status":
                    row.get(
                        "status"
                    ),
            }
        )


    status: list[dict[str, Any]] = []

    for row in status_rows:

        status.append(
            {
                "status":
                    row.get(
                        "status"
                    ),

                "observations":
                    as_int(
                        row.get(
                            "observations"
                        )
                    ),

                "production_tonnes":
                    as_float(
                        row.get(
                            "production_tonnes"
                        )
                    ),

                "share_pct":
                    as_float(
                        row.get(
                            "share_pct"
                        )
                    ),
            }
        )


    response = {
        "country":
            "India",

        "species":
            "Litopenaeus vannamei",

        "source":
            "FAO",

        "dataset":
            "Global Aquaculture Production",

        "release":
            benchmark.get(
                "release"
            ),

        "data_through":
            benchmark.get(
                "data_through"
            ),

        "first_year":
            benchmark.get(
                "first_year"
            ),

        "last_year":
            benchmark.get(
                "last_year"
            ),

        "year_count":
            benchmark.get(
                "year_count"
            ),

        "missing_years":
            benchmark.get(
                "missing_years",
                [],
            ),

        "first_year_production_tonnes":
            benchmark.get(
                "first_year_production_tonnes"
            ),

        "last_year_production_tonnes":
            benchmark.get(
                "last_year_production_tonnes"
            ),

        "endpoint_growth_cagr_pct":
            benchmark.get(
                "cagr_pct"
            ),

        "official_observations":
            benchmark.get(
                "official_observations"
            ),

        "imputed_observations":
            benchmark.get(
                "imputed_observations"
            ),

        "yearly_production":
            yearly,

        "environment_breakdown":
            environments,

        "status_breakdown":
            status,

        "source_information":
            {
                "provider":
                    source_metadata.get(
                        "provider"
                    ),

                "database":
                    source_metadata.get(
                        "database"
                    ),

                "coverage":
                    source_metadata.get(
                        "coverage"
                    ),

                "frequency":
                    source_metadata.get(
                        "frequency"
                    ),

                "license":
                    source_metadata.get(
                        "license"
                    ),

                "status":
                    source_metadata.get(
                        "status"
                    ),
            },

        "scientific_boundary":
            {
                "source_type":
                    "official_aggregated_statistics",

                "real_world":
                    True,

                "pond_level":
                    False,

                "farm_level":
                    False,

                "synthetic":
                    False,

                "model_training":
                    False,

                "prediction_accuracy_claim":
                    False,

                "missing_years_interpolated":
                    False,

                "status_preserved":
                    True,
            },
    }

    return response

