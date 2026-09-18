from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from catboost import CatBoostRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.model_selection import train_test_split


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


DATASET = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "production-synthetic-v1.1.csv"
)


MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)


REPORT_DIR = (
    PROJECT_ROOT
    / "data"
    / "reports"
)


TARGET = "production_kg"


# ============================================================
# DEPLOYMENT-SAFE FEATURES
# ============================================================

FEATURES = [
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


# These represent information that is only known after
# the production outcome has occurred. They must not be
# used as prediction features.

FORBIDDEN_FEATURES = {
    "harvest_average_weight_g",
    "surviving_count",
    "mortality_rate",
}


SEED = 20260916


def calculate_metrics(
    y_true,
    y_pred,
) -> dict[str, float]:

    return {
        "mae": float(
            mean_absolute_error(
                y_true,
                y_pred,
            )
        ),

        "rmse": float(
            np.sqrt(
                mean_squared_error(
                    y_true,
                    y_pred,
                )
            )
        ),

        "r2": float(
            r2_score(
                y_true,
                y_pred,
            )
        ),
    }


def check_for_leakage() -> None:

    overlap = (
        set(FEATURES)
        &
        FORBIDDEN_FEATURES
    )

    if overlap:

        raise RuntimeError(
            "Prediction feature leakage detected: "
            +
            ", ".join(
                sorted(overlap)
            )
        )


def main() -> None:

    print(
        "============================================================"
    )

    print(
        " AquaLife CatBoost V0.2"
    )

    print(
        " Deployment-safe feature training"
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # Leakage check.
    # --------------------------------------------------------

    check_for_leakage()

    print(
        "Leakage check: PASS"
    )

    # --------------------------------------------------------
    # Dataset.
    # --------------------------------------------------------

    if not DATASET.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    df = pd.read_csv(
        DATASET
    )

    print(
        "Dataset rows:",
        len(df),
    )

    # --------------------------------------------------------
    # Column check.
    # --------------------------------------------------------

    required_columns = (
        FEATURES
        +
        [TARGET]
    )

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise RuntimeError(
            "Missing dataset columns: "
            +
            ", ".join(missing)
        )

    # --------------------------------------------------------
    # Missing-value check.
    # --------------------------------------------------------

    missing_cells = int(
        df[
            required_columns
        ]
        .isna()
        .sum()
        .sum()
    )

    if missing_cells > 0:

        raise RuntimeError(
            f"Dataset contains {missing_cells} "
            "missing cells."
        )

    # --------------------------------------------------------
    # Inputs and target.
    # --------------------------------------------------------

    X = df[
        FEATURES
    ]

    y = df[
        TARGET
    ]

    # --------------------------------------------------------
    # First split: 80/20 train/test.
    # --------------------------------------------------------

    (
        X_train_full,
        X_test,
        y_train_full,
        y_test,
    ) = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=SEED,
    )

    # --------------------------------------------------------
    # Second split: training/validation.
    # --------------------------------------------------------

    (
        X_train,
        X_valid,
        y_train,
        y_valid,
    ) = train_test_split(
        X_train_full,
        y_train_full,
        test_size=0.20,
        random_state=SEED,
    )

    print(
        "Train:",
        len(X_train),
    )

    print(
        "Validation:",
        len(X_valid),
    )

    print(
        "Test:",
        len(X_test),
    )

    # --------------------------------------------------------
    # Model.
    # --------------------------------------------------------

    model = CatBoostRegressor(

        loss_function="RMSE",

        eval_metric="RMSE",

        iterations=1200,

        learning_rate=0.04,

        depth=8,

        l2_leaf_reg=5.0,

        random_seed=SEED,

        random_strength=1.0,

        verbose=False,

        allow_writing_files=False,
    )

    print()
    print(
        "Training CatBoost..."
    )

    model.fit(

        X_train,
        y_train,

        eval_set=(
            X_valid,
            y_valid,
        ),

        use_best_model=True,

        early_stopping_rounds=100,
    )

    # --------------------------------------------------------
    # Validation evaluation.
    # --------------------------------------------------------

    validation_pred = model.predict(
        X_valid
    )

    validation_metrics = (
        calculate_metrics(
            y_valid,
            validation_pred,
        )
    )

    # --------------------------------------------------------
    # Final test evaluation.
    # --------------------------------------------------------

    test_pred = model.predict(
        X_test
    )

    test_metrics = (
        calculate_metrics(
            y_test,
            test_pred,
        )
    )

    # --------------------------------------------------------
    # Feature importance.
    # --------------------------------------------------------

    importance = (
        model.get_feature_importance()
    )

    feature_importance = sorted(
        [
            {
                "feature":
                    feature,

                "importance":
                    float(score),
            }

            for feature, score
            in zip(
                FEATURES,
                importance,
            )
        ],
        key=lambda item:
            item["importance"],
        reverse=True,
    )

    # --------------------------------------------------------
    # Output directories.
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Model artifacts.
    # --------------------------------------------------------

    model_path = (
        MODEL_DIR
        / "production-catboost-v0.2.cbm"
    )

    joblib_path = (
        MODEL_DIR
        / "production-catboost-v0.2.joblib"
    )

    report_path = (
        REPORT_DIR
        / "production-catboost-v0.2-report.json"
    )

    model.save_model(
        model_path
    )

    joblib.dump(
        model,
        joblib_path,
    )

    # --------------------------------------------------------
    # Experiment report.
    # --------------------------------------------------------

    report = {

        "experiment": {

            "name":
                "production-catboost-deployment-safe",

            "version":
                "0.2.0",

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "dataset":
                str(DATASET),

            "dataset_version":
                "production-synthetic-v1.1",

            "rows":
                int(len(df)),

            "seed":
                SEED,
        },


        "target":
            TARGET,


        "features": {

            "deployment_safe":
                FEATURES,

            "excluded_future_information":
                sorted(
                    FORBIDDEN_FEATURES
                ),
        },


        "split": {

            "train":
                int(len(X_train)),

            "validation":
                int(len(X_valid)),

            "test":
                int(len(X_test)),
        },


        "validation_metrics":
            validation_metrics,


        "test_metrics":
            test_metrics,


        "best_iteration":
            int(
                model.get_best_iteration()
            ),


        "feature_importance":
            feature_importance,


        "model": {

            "library":
                "catboost",

            "class":
                "CatBoostRegressor",

            "loss":
                "RMSE",

            "artifact":
                str(model_path),

            "joblib_artifact":
                str(joblib_path),
        },


        "leakage_control": {

            "checked":
                True,

            "future_target_components_used":
                False,
        },


        "scientific_boundary": {

            "training_data_type":
                "synthetic",

            "real_world_validation":
                False,

            "real_world_accuracy_claim":
                False,

            "interpretation":
                "Metrics measure performance on "
                "synthetic scenarios generated by "
                "the AquaLife synthetic generator.",
        },
    }


    with report_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Console results.
    # --------------------------------------------------------

    print()
    print(
        "VALIDATION METRICS:"
    )

    print(
        json.dumps(
            validation_metrics,
            indent=2,
        )
    )

    print()
    print(
        "TEST METRICS:"
    )

    print(
        json.dumps(
            test_metrics,
            indent=2,
        )
    )

    print()
    print(
        "BEST ITERATION:",
        model.get_best_iteration(),
    )

    print()
    print(
        "TOP FEATURES:"
    )

    for item in feature_importance[:10]:

        print(
            f"{item['feature']}: "
            f"{item['importance']:.6f}"
        )

    print()
    print(
        "MODEL:",
        model_path,
    )

    print(
        "REPORT:",
        report_path,
    )


if __name__ == "__main__":
    main()
