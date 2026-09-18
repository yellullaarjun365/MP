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


PROJECT_ROOT = Path(__file__).resolve().parents[3]

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

RUN_DIR = (
    PROJECT_ROOT
    / "ml"
    / "runs"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "data"
    / "reports"
)


TARGET = "production_kg"


FEATURES = [
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
    "density_growth_multiplier",
    "effective_growth_rate_g_week",
    "harvest_average_weight_g",
    "surviving_count",
]


SEED = 20260916


def rmse(
    y_true,
    y_pred,
) -> float:

    return float(
        np.sqrt(
            mean_squared_error(
                y_true,
                y_pred,
            )
        )
    )


def metrics(
    y_true,
    y_pred,
) -> dict:

    return {
        "mae": float(
            mean_absolute_error(
                y_true,
                y_pred,
            )
        ),

        "rmse": rmse(
            y_true,
            y_pred,
        ),

        "r2": float(
            r2_score(
                y_true,
                y_pred,
            )
        ),
    }


def main() -> None:

    if not DATASET.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    df = pd.read_csv(
        DATASET
    )

    missing = [
        column
        for column in (
            FEATURES + [TARGET]
        )
        if column not in df.columns
    ]

    if missing:

        raise RuntimeError(
            "Missing columns: "
            + ", ".join(missing)
        )

    X = df[
        FEATURES
    ]

    y = df[
        TARGET
    ]

    # --------------------------------------------------------
    # Train/test first.
    # --------------------------------------------------------

    X_train_full, X_test, y_train_full, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=SEED,
        )
    )

    # --------------------------------------------------------
    # Validation split comes ONLY from training data.
    # --------------------------------------------------------

    X_train, X_valid, y_train, y_valid = (
        train_test_split(
            X_train_full,
            y_train_full,
            test_size=0.20,
            random_state=SEED,
        )
    )

    print(
        "Dataset rows:",
        len(df),
    )

    print(
        "Train rows:",
        len(X_train),
    )

    print(
        "Validation rows:",
        len(X_valid),
    )

    print(
        "Test rows:",
        len(X_test),
    )

    model = CatBoostRegressor(
        loss_function="RMSE",
        eval_metric="RMSE",

        iterations=800,

        learning_rate=0.05,

        depth=8,

        l2_leaf_reg=5.0,

        random_seed=SEED,

        verbose=False,

        allow_writing_files=False,
    )

    model.fit(
        X_train,
        y_train,

        eval_set=(
            X_valid,
            y_valid,
        ),

        use_best_model=True,
        early_stopping_rounds=80,
    )

    # --------------------------------------------------------
    # Validation metrics.
    # --------------------------------------------------------

    valid_pred = model.predict(
        X_valid
    )

    valid_metrics = metrics(
        y_valid,
        valid_pred,
    )

    # --------------------------------------------------------
    # Final untouched test evaluation.
    # --------------------------------------------------------

    test_pred = model.predict(
        X_test
    )

    test_metrics = metrics(
        y_test,
        test_pred,
    )

    # --------------------------------------------------------
    # Feature importance.
    # --------------------------------------------------------

    importance = model.get_feature_importance()

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
    # Save model.
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        MODEL_DIR
        / "production-catboost-v0.1.cbm"
    )

    model.save_model(
        model_path
    )

    # Save a joblib wrapper copy for future service integration.
    joblib_path = (
        MODEL_DIR
        / "production-catboost-v0.1.joblib"
    )

    joblib.dump(
        model,
        joblib_path,
    )

    # --------------------------------------------------------
    # Report.
    # --------------------------------------------------------

    report = {
        "experiment": {
            "name":
                "production-catboost-baseline",

            "version":
                "0.1.0",

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

            "features":
                FEATURES,

            "target":
                TARGET,
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
            valid_metrics,

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

            "model_class":
                "CatBoostRegressor",

            "loss":
                "RMSE",

            "artifact":
                str(model_path),

            "joblib_artifact":
                str(joblib_path),
        },

        "scientific_boundary": {
            "training_data":
                "synthetic",

            "real_world_validation":
                False,

            "real_world_accuracy_claim":
                False,

            "interpretation":
                "Metrics measure performance on "
                "synthetic data generated by the "
                "AquaLife V1.1 generator."
        },
    }

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        REPORT_DIR
        / "production-catboost-v0.1-report.json"
    )

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
        )

    print()
    print(
        "VALIDATION METRICS:"
    )

    print(
        json.dumps(
            valid_metrics,
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
            f"{item['importance']:.4f}"
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
