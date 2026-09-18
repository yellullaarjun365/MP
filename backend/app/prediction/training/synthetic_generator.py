from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

DEFAULT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "manifests"
    / "production-evidence-v1.json"
)

DEFAULT_DATASET_DIR = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
)

DEFAULT_REPORT_DIR = (
    PROJECT_ROOT
    / "data"
    / "reports"
)


# ============================================================
# OPERATIONAL GENERATOR BOUNDS
# ============================================================
#
# V1 is explicitly a pond grow-out generator.
#
# The evidence manifest contains a broader upper bound for
# stocking density, but V1 operationalizes the pond regime
# at 25-150 PL/m2.
#
# This is a synthetic development rule, not a real-world
# prediction model.
# ============================================================

POND_DENSITY_MIN = 25.0
POND_DENSITY_MAX = 150.0

INITIAL_WEIGHT_MIN = 0.01
INITIAL_WEIGHT_MAX = 2.0

POND_AREA_MIN = 100.0
POND_AREA_MAX = 10000.0

POND_DEPTH_MIN = 0.8
POND_DEPTH_MAX = 2.5

CULTURE_DAYS_MIN = 90.0
CULTURE_DAYS_MAX = 180.0

SURVIVAL_MIN = 0.50
SURVIVAL_MAX = 0.95

GROWTH_RATE_MIN = 0.50
GROWTH_RATE_MAX = 3.00


# ============================================================
# DENSITY EFFECT PARAMETERS
# ============================================================
#
# The density effect is intentionally modest.
#
# It reduces effective growth as density rises rather than
# forcing a deterministic outcome.
#
# Reference points come from the 25/35/50 PL/m2 AGRIS study,
# where mean harvest weight decreased with density.
#
# This is a synthetic relationship for dataset generation,
# not a fitted empirical production model.
# ============================================================

DENSITY_REFERENCE = 25.0
DENSITY_EFFECT_MAX = 0.28


# ============================================================
# MANIFEST
# ============================================================


def load_manifest(
    path: str | Path = DEFAULT_MANIFEST,
) -> dict:

    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:

        return json.load(file)


def validate_manifest(
    manifest: dict,
) -> list[str]:

    errors: list[str] = []

    variables = manifest.get(
        "variables",
        {},
    )

    policy = manifest.get(
        "generator_policy"
    )

    if not manifest.get(
        "sources"
    ):
        errors.append(
            "manifest.sources is empty"
        )

    if not manifest.get(
        "relationships"
    ):
        errors.append(
            "manifest.relationships is empty"
        )

    if not manifest.get(
        "constraints"
    ):
        errors.append(
            "manifest.constraints is empty"
        )

    if policy is None:
        errors.append(
            "manifest.generator_policy is missing"
        )
        return errors

    enabled = policy.get(
        "enabled_variables",
        [],
    )

    relation_only = policy.get(
        "relation_only_variables",
        [],
    )

    overlap = (
        set(enabled)
        & set(relation_only)
    )

    if overlap:

        errors.append(
            "enabled/relation-only overlap: "
            + ", ".join(
                sorted(overlap)
            )
        )

    for name in enabled:

        definition = variables.get(
            name
        )

        if definition is None:

            errors.append(
                f"{name}: missing definition"
            )

            continue

        if not definition.get(
            "source_ids"
        ):

            errors.append(
                f"{name}: missing source_ids"
            )

        if definition.get(
            "min"
        ) is None:

            errors.append(
                f"{name}: missing min"
            )

        if definition.get(
            "max"
        ) is None:

            errors.append(
                f"{name}: missing max"
            )

        if not definition.get(
            "distribution"
        ):

            errors.append(
                f"{name}: missing distribution"
            )

        if definition.get(
            "sampling_enabled"
        ) is not True:

            errors.append(
                f"{name}: sampling_enabled must be true"
            )

    for name in relation_only:

        definition = variables.get(
            name
        )

        if definition is None:

            errors.append(
                f"{name}: missing definition"
            )

            continue

        if definition.get(
            "sampling_enabled"
        ) is not False:

            errors.append(
                f"{name}: sampling_enabled must be false"
            )

    target_policy = manifest.get(
        "target_policy"
    )

    if target_policy is None:

        errors.append(
            "target_policy is missing"
        )

    else:

        if target_policy.get(
            "name"
        ) != "production_kg":

            errors.append(
                "target_policy.name must be "
                "production_kg"
            )

        if target_policy.get(
            "type"
        ) != "derived_target":

            errors.append(
                "production_kg must be derived_target"
            )

    return errors


# ============================================================
# DISTRIBUTIONS
# ============================================================


def sample_truncated_normal(
    rng: np.random.Generator,
    mean: float,
    std: float,
    minimum: float,
    maximum: float,
    size: int,
) -> np.ndarray:

    values = rng.normal(
        mean,
        std,
        size,
    )

    return np.clip(
        values,
        minimum,
        maximum,
    )


def sample_log_uniform(
    rng: np.random.Generator,
    minimum: float,
    maximum: float,
    size: int,
) -> np.ndarray:

    return np.exp(
        rng.uniform(
            np.log(minimum),
            np.log(maximum),
            size,
        )
    )


def sample_truncated_beta(
    rng: np.random.Generator,
    alpha: float,
    beta: float,
    minimum: float,
    maximum: float,
    size: int,
) -> np.ndarray:

    values = rng.beta(
        alpha,
        beta,
        size,
    )

    return (
        minimum
        +
        values
        *
        (
            maximum
            -
            minimum
        )
    )


def sample_stocking_density(
    rng: np.random.Generator,
    size: int,
) -> np.ndarray:

    selector = rng.uniform(
        0.0,
        1.0,
        size,
    )

    result = np.empty(
        size,
        dtype=float,
    )

    low_mask = selector < 0.70

    low_count = int(
        low_mask.sum()
    )

    high_count = (
        size -
        low_count
    )

    if low_count > 0:

        result[low_mask] = (
            rng.uniform(
                25.0,
                80.0,
                low_count,
            )
        )

    if high_count > 0:

        result[~low_mask] = (
            rng.uniform(
                80.0,
                150.0,
                high_count,
            )
        )

    return result


# ============================================================
# BIOLOGICAL DERIVATIONS
# ============================================================


def density_growth_multiplier(
    stocking_density_per_m2: np.ndarray,
) -> np.ndarray:
    """
    Convert stocking density into a modest growth-pressure
    multiplier.

    The function is deliberately smooth and bounded.

    25 PL/m2 -> approximately 1.00
    150 PL/m2 -> approximately 0.72

    This does NOT assert that every real farm follows this exact
    curve. It is an evidence-informed synthetic relationship
    used to produce non-independent training scenarios.
    """

    normalized = (
        stocking_density_per_m2
        -
        DENSITY_REFERENCE
    ) / (
        POND_DENSITY_MAX
        -
        DENSITY_REFERENCE
    )

    normalized = np.clip(
        normalized,
        0.0,
        1.0,
    )

    multiplier = (
        1.0
        -
        DENSITY_EFFECT_MAX
        *
        normalized
    )

    return multiplier


def calculate_harvest_weight(
    initial_weight_g: np.ndarray,
    growth_rate_g_week: np.ndarray,
    culture_days: np.ndarray,
) -> np.ndarray:

    weeks = (
        culture_days
        /
        7.0
    )

    grams_to_20 = np.maximum(
        20.0 -
        initial_weight_g,
        0.0,
    )

    weeks_to_20 = (
        grams_to_20
        /
        growth_rate_g_week
    )

    final_weight = np.empty_like(
        initial_weight_g
    )

    below_20 = (
        weeks <= weeks_to_20
    )

    final_weight[
        below_20
    ] = (
        initial_weight_g[
            below_20
        ]
        +
        growth_rate_g_week[
            below_20
        ]
        *
        weeks[
            below_20
        ]
    )

    remaining_weeks = (
        weeks
        -
        weeks_to_20
    )

    final_weight[
        ~below_20
    ] = (
        20.0
        +
        remaining_weeks[
            ~below_20
        ]
    )

    return np.maximum(
        final_weight,
        initial_weight_g,
    )


def derive_harvest(
    stocking_count: np.ndarray,
    survival_rate: np.ndarray,
    harvest_weight_g: np.ndarray,
) -> tuple[
    np.ndarray,
    np.ndarray,
]:

    surviving_count = np.rint(
        stocking_count
        *
        survival_rate
    ).astype(
        np.int64
    )

    production_kg = (
        surviving_count
        *
        harvest_weight_g
        /
        1000.0
    )

    return (
        surviving_count,
        production_kg,
    )


# ============================================================
# DATASET GENERATION
# ============================================================


def generate_synthetic_dataset(
    manifest: dict,
    rows: int = 10000,
    seed: int | None = None,
) -> pd.DataFrame:

    if rows <= 0:
        raise ValueError(
            "rows must be greater than zero"
        )

    errors = validate_manifest(
        manifest
    )

    if errors:

        raise ValueError(
            "Generator manifest is invalid:\n"
            +
            "\n".join(
                f"- {error}"
                for error in errors
            )
        )

    if seed is None:

        seed = int(
            manifest.get(
                "random_seed",
                20260916,
            )
        )

    rng = np.random.default_rng(
        seed
    )

    # --------------------------------------------------------
    # Farm geometry.
    # --------------------------------------------------------

    pond_area_m2 = (
        sample_log_uniform(
            rng,
            POND_AREA_MIN,
            POND_AREA_MAX,
            rows,
        )
    )

    pond_depth_m = (
        sample_truncated_normal(
            rng,
            mean=1.5,
            std=0.28,
            minimum=POND_DEPTH_MIN,
            maximum=POND_DEPTH_MAX,
            size=rows,
        )
    )

    # --------------------------------------------------------
    # Stocking density.
    # --------------------------------------------------------

    stocking_density_per_m2 = (
        sample_stocking_density(
            rng,
            rows,
        )
    )

    # --------------------------------------------------------
    # Initial animal size.
    # --------------------------------------------------------

    initial_average_weight_g = (
        sample_log_uniform(
            rng,
            INITIAL_WEIGHT_MIN,
            INITIAL_WEIGHT_MAX,
            rows,
        )
    )

    # --------------------------------------------------------
    # Culture duration.
    # --------------------------------------------------------

    culture_days = np.rint(
        sample_truncated_normal(
            rng,
            mean=125.0,
            std=18.0,
            minimum=CULTURE_DAYS_MIN,
            maximum=CULTURE_DAYS_MAX,
            size=rows,
        )
    )

    # --------------------------------------------------------
    # Survival.
    # --------------------------------------------------------

    survival_rate = (
        sample_truncated_beta(
            rng,
            alpha=8.0,
            beta=2.0,
            minimum=SURVIVAL_MIN,
            maximum=SURVIVAL_MAX,
            size=rows,
        )
    )

    # --------------------------------------------------------
    # Growth rate.
    # --------------------------------------------------------

    growth_rate_g_week = (
        sample_truncated_normal(
            rng,
            mean=1.35,
            std=0.35,
            minimum=GROWTH_RATE_MIN,
            maximum=GROWTH_RATE_MAX,
            size=rows,
        )
    )

    # --------------------------------------------------------
    # Correlated derived values.
    # --------------------------------------------------------

    stocking_count = np.rint(
        pond_area_m2
        *
        stocking_density_per_m2
    ).astype(
        np.int64
    )

    initial_biomass_kg = (
        stocking_count
        *
        initial_average_weight_g
        /
        1000.0
    )

    density_multiplier = (
        density_growth_multiplier(
            stocking_density_per_m2
        )
    )

    effective_growth_rate_g_week = (
        growth_rate_g_week
        *
        density_multiplier
    )

    harvest_average_weight_g = (
        calculate_harvest_weight(
            initial_average_weight_g,
            effective_growth_rate_g_week,
            culture_days,
        )
    )

    surviving_count, production_kg = (
        derive_harvest(
            stocking_count,
            survival_rate,
            harvest_average_weight_g,
        )
    )

    mortality_rate = (
        1.0 -
        survival_rate
    )

    production_kg_per_ha = (
        production_kg
        /
        pond_area_m2
        *
        10000.0
    )

    return pd.DataFrame(
        {
            "species": [
                "Litopenaeus vannamei"
            ]
            *
            rows,

            "pond_area_m2":
                pond_area_m2,

            "pond_depth_m":
                pond_depth_m,

            "stocking_density_per_m2":
                stocking_density_per_m2,

            "stocking_count":
                stocking_count,

            "initial_average_weight_g":
                initial_average_weight_g,

            "initial_biomass_kg":
                initial_biomass_kg,

            "culture_days":
                culture_days,

            "survival_rate":
                survival_rate,

            "mortality_rate":
                mortality_rate,

            "growth_rate_g_week":
                growth_rate_g_week,

            "density_growth_multiplier":
                density_multiplier,

            "effective_growth_rate_g_week":
                effective_growth_rate_g_week,

            "harvest_average_weight_g":
                harvest_average_weight_g,

            "surviving_count":
                surviving_count,

            "production_kg":
                production_kg,

            "production_kg_per_ha":
                production_kg_per_ha,
        }
    )


# ============================================================
# DATASET VALIDATION
# ============================================================


def validate_dataset(
    dataframe: pd.DataFrame,
) -> dict:

    required_columns = [
        "species",
        "pond_area_m2",
        "pond_depth_m",
        "stocking_density_per_m2",
        "stocking_count",
        "initial_average_weight_g",
        "initial_biomass_kg",
        "culture_days",
        "survival_rate",
        "mortality_rate",
        "growth_rate_g_week",
        "harvest_average_weight_g",
        "surviving_count",
        "production_kg",
        "production_kg_per_ha",
    ]

    report = {
        "status": "PASS",
        "rows": int(
            len(dataframe)
        ),
        "checks": {},
        "failures": [],
    }

    def record_check(
        name: str,
        condition: bool,
    ) -> None:

        report["checks"][name] = bool(
            condition
        )

        if not condition:

            report["failures"].append(
                name
            )

    record_check(
        "required_columns",
        all(
            column in dataframe.columns
            for column in required_columns
        ),
    )

    if dataframe.empty:

        record_check(
            "non_empty_dataset",
            False,
        )

        report["status"] = "FAIL"

        return report

    numeric_columns = [
        "pond_area_m2",
        "pond_depth_m",
        "stocking_density_per_m2",
        "stocking_count",
        "initial_average_weight_g",
        "initial_biomass_kg",
        "culture_days",
        "survival_rate",
        "mortality_rate",
        "growth_rate_g_week",
        "harvest_average_weight_g",
        "surviving_count",
        "production_kg",
        "production_kg_per_ha",
    ]

    record_check(
        "finite_numeric_values",
        bool(
            np.isfinite(
                dataframe[
                    numeric_columns
                ].to_numpy()
            ).all()
        ),
    )

    record_check(
        "pond_area_range",
        bool(
            dataframe[
                "pond_area_m2"
            ].between(
                POND_AREA_MIN,
                POND_AREA_MAX,
            ).all()
        ),
    )

    record_check(
        "pond_depth_range",
        bool(
            dataframe[
                "pond_depth_m"
            ].between(
                POND_DEPTH_MIN,
                POND_DEPTH_MAX,
            ).all()
        ),
    )

    record_check(
        "stocking_density_range",
        bool(
            dataframe[
                "stocking_density_per_m2"
            ].between(
                POND_DENSITY_MIN,
                POND_DENSITY_MAX,
            ).all()
        ),
    )

    record_check(
        "initial_weight_range",
        bool(
            dataframe[
                "initial_average_weight_g"
            ].between(
                INITIAL_WEIGHT_MIN,
                INITIAL_WEIGHT_MAX,
            ).all()
        ),
    )

    record_check(
        "culture_days_range",
        bool(
            dataframe[
                "culture_days"
            ].between(
                CULTURE_DAYS_MIN,
                CULTURE_DAYS_MAX,
            ).all()
        ),
    )

    record_check(
        "survival_range",
        bool(
            dataframe[
                "survival_rate"
            ].between(
                SURVIVAL_MIN,
                SURVIVAL_MAX,
            ).all()
        ),
    )

    record_check(
        "growth_rate_range",
        bool(
            dataframe[
                "growth_rate_g_week"
            ].between(
                GROWTH_RATE_MIN,
                GROWTH_RATE_MAX,
            ).all()
        ),
    )

    record_check(
        "density_multiplier_range",
        bool(
            dataframe[
                "density_growth_multiplier"
            ].between(
                1.0 - DENSITY_EFFECT_MAX,
                1.0,
            ).all()
        ),
    )

    record_check(
        "effective_growth_not_above_base",
        bool(
            (
                dataframe[
                    "effective_growth_rate_g_week"
                ]
                <=
                dataframe[
                    "growth_rate_g_week"
                ]
            ).all()
        ),
    )

    record_check(
        "effective_growth_positive",
        bool(
            (
                dataframe[
                    "effective_growth_rate_g_week"
                ] > 0
            ).all()
        ),
    )

    record_check(
        "nonnegative_production",
        bool(
            (
                dataframe[
                    "production_kg"
                ] >= 0
            ).all()
        ),
    )

    # --------------------------------------------------------
    # Identity: stocking count.
    # --------------------------------------------------------

    expected_stocking = np.rint(
        dataframe[
            "pond_area_m2"
        ]
        *
        dataframe[
            "stocking_density_per_m2"
        ]
    ).astype(
        np.int64
    )

    record_check(
        "stocking_identity",
        bool(
            (
                expected_stocking
                ==
                dataframe[
                    "stocking_count"
                ]
            ).all()
        ),
    )

    # --------------------------------------------------------
    # Identity: initial biomass.
    # --------------------------------------------------------

    expected_initial_biomass = (
        dataframe[
            "stocking_count"
        ]
        *
        dataframe[
            "initial_average_weight_g"
        ]
        /
        1000.0
    )

    record_check(
        "initial_biomass_identity",
        bool(
            np.allclose(
                expected_initial_biomass,
                dataframe[
                    "initial_biomass_kg"
                ],
                rtol=1e-9,
                atol=1e-9,
            )
        ),
    )

    # --------------------------------------------------------
    # Identity: survival.
    # --------------------------------------------------------

    expected_surviving = np.rint(
        dataframe[
            "stocking_count"
        ]
        *
        dataframe[
            "survival_rate"
        ]
    ).astype(
        np.int64
    )

    record_check(
        "survival_identity",
        bool(
            (
                expected_surviving
                ==
                dataframe[
                    "surviving_count"
                ]
            ).all()
        ),
    )

    # --------------------------------------------------------
    # Identity: mortality.
    # --------------------------------------------------------

    record_check(
        "mortality_identity",
        bool(
            np.allclose(
                dataframe[
                    "mortality_rate"
                ],
                1.0
                -
                dataframe[
                    "survival_rate"
                ],
                rtol=1e-12,
                atol=1e-12,
            )
        ),
    )

    # --------------------------------------------------------
    # Identity: production.
    # --------------------------------------------------------

    expected_production = (
        dataframe[
            "surviving_count"
        ]
        *
        dataframe[
            "harvest_average_weight_g"
        ]
        /
        1000.0
    )

    record_check(
        "production_identity",
        bool(
            np.allclose(
                expected_production,
                dataframe[
                    "production_kg"
                ],
                rtol=1e-9,
                atol=1e-9,
            )
        ),
    )

    # --------------------------------------------------------
    # Biological monotonicity.
    # --------------------------------------------------------

    record_check(
        "weight_not_below_initial",
        bool(
            (
                dataframe[
                    "harvest_average_weight_g"
                ]
                >=
                dataframe[
                    "initial_average_weight_g"
                ]
            ).all()
        ),
    )

    # --------------------------------------------------------
    # Production density.
    # --------------------------------------------------------

    record_check(
        "production_per_ha_nonnegative",
        bool(
            (
                dataframe[
                    "production_kg_per_ha"
                ] >= 0
            ).all()
        ),
    )

    # --------------------------------------------------------
    # Dataset distribution summary.
    # --------------------------------------------------------

    report[
        "production_summary"
    ] = {
        "min_kg": float(
            dataframe[
                "production_kg"
            ].min()
        ),
        "median_kg": float(
            dataframe[
                "production_kg"
            ].median()
        ),
        "mean_kg": float(
            dataframe[
                "production_kg"
            ].mean()
        ),
        "max_kg": float(
            dataframe[
                "production_kg"
            ].max()
        ),
    }

    report[
        "production_per_ha_summary"
    ] = {
        "min_kg_per_ha": float(
            dataframe[
                "production_kg_per_ha"
            ].min()
        ),
        "median_kg_per_ha": float(
            dataframe[
                "production_kg_per_ha"
            ].median()
        ),
        "mean_kg_per_ha": float(
            dataframe[
                "production_kg_per_ha"
            ].mean()
        ),
        "max_kg_per_ha": float(
            dataframe[
                "production_kg_per_ha"
            ].max()
        ),
    }

    if report["failures"]:

        report["status"] = "FAIL"

    return report


# ============================================================
# ARTIFACT GENERATION
# ============================================================


def generate_artifacts(
    rows: int = 10000,
    seed: int = 20260916,
    manifest_path: str | Path = DEFAULT_MANIFEST,
) -> dict:

    manifest = load_manifest(
        manifest_path
    )

    dataframe = (
        generate_synthetic_dataset(
            manifest=manifest,
            rows=rows,
            seed=seed,
        )
    )

    validation = validate_dataset(
        dataframe
    )

    DEFAULT_DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    DEFAULT_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset_path = (
        DEFAULT_DATASET_DIR
        /
        "production-synthetic-v1.csv"
    )

    validation_path = (
        DEFAULT_REPORT_DIR
        /
        "production-synthetic-v1-validation.json"
    )

    metadata_path = (
        DEFAULT_REPORT_DIR
        /
        "production-synthetic-v1-metadata.json"
    )

    dataframe.to_csv(
        dataset_path,
        index=False,
    )

    validation_payload = {
        "schema_version":
            "synthetic-validation-v1",

        "generator_version":
            "1.0.0",

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "rows":
            int(len(dataframe)),

        "seed":
            int(seed),

        "species":
            manifest["species"],

        "target":
            manifest["target"],

        "validation":
            validation,

        "scientific_boundary": {
            "training_data_type":
                "synthetic",

            "real_world_validation":
                False,

            "real_world_accuracy_claim_allowed":
                False,
        },
    }

    metadata_payload = {
        "schema_version":
            "synthetic-dataset-v1",

        "generator_version":
            "1.0.0",

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "rows":
            int(len(dataframe)),

        "seed":
            int(seed),

        "species":
            manifest["species"],

        "target":
            manifest["target"],

        "manifest_schema":
            manifest["schema_version"],

        "operational_bounds": {
            "pond_density_min":
                POND_DENSITY_MIN,

            "pond_density_max":
                POND_DENSITY_MAX,

            "pond_area_min":
                POND_AREA_MIN,

            "pond_area_max":
                POND_AREA_MAX,
        },

        "scientific_boundary": {
            "training_data_type":
                "synthetic",

            "real_world_validation":
                False,

            "purpose":
                "model development and "
                "internal benchmarking",
        },
    }

    with validation_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            validation_payload,
            file,
            indent=2,
        )

    with metadata_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata_payload,
            file,
            indent=2,
        )

    return {
        "dataset_path":
            str(dataset_path),

        "validation_path":
            str(validation_path),

        "metadata_path":
            str(metadata_path),

        "rows":
            int(len(dataframe)),

        "validation":
            validation,
    }


# ============================================================
# CLI
# ============================================================


if __name__ == "__main__":

    manifest = load_manifest()

    seed = int(
        manifest.get(
            "random_seed",
            20260916,
        )
    )

    result = generate_artifacts(
        rows=10000,
        seed=seed,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    if result[
        "validation"
    ][
        "status"
    ] != "PASS":

        raise SystemExit(
            "Synthetic dataset validation FAILED."
        )
