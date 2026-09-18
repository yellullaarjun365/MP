from __future__ import annotations

import csv
import json
import math
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


ROOT = Path("/benchmark")
DATA = ROOT / "data"
OUTPUT = Path("/results")
OUTPUT.mkdir(parents=True, exist_ok=True)


FILES = [
    DATA / "A1_sample_90days.csv",
    DATA / "B1_sample_90days.csv",
    DATA / "C1_sample_90days.csv",
]


# ============================================================
# FIXED EXPERIMENT CONTRACT
# ============================================================

HISTORY_STEPS = 288
HORIZON_STEPS = 288
INTERVAL_MINUTES = 15

TRAIN_FRACTION = 0.70
VALIDATION_FRACTION = 0.15
TEST_FRACTION = 0.15

RANDOM_SEED = 42

BATCH_SIZE = 64
EPOCHS = 60
LEARNING_RATE = 0.001

HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.20

PATIENCE = 10

FEATURES = [
    "DO_mg_L",
    "TAN_mg_L",
    "NO2_mg_L",
    "pH",
    "turbidity_NTU",
    "temp_C",
    "feed_rate_kg_h",
    "aeration_duty_pct",
    "exchange_flow_m3_h",
]

TARGET = "DO_mg_L"

DEVICE = torch.device("cpu")


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def seed_everything(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


seed_everything(RANDOM_SEED)


def read_farm(path: Path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = reader.fieldnames or []

    required = set(FEATURES + ["timestamp", "farm_id"])
    missing = sorted(required - set(columns))

    if missing:
        raise RuntimeError(
            f"{path.name} missing columns: {missing}"
        )

    timestamps = [
        row["timestamp"]
        for row in rows
    ]

    if timestamps != sorted(timestamps):
        raise RuntimeError(
            f"{path.name} timestamps are not ordered."
        )

    farm_ids = sorted(
        {
            row["farm_id"]
            for row in rows
        }
    )

    if len(farm_ids) != 1:
        raise RuntimeError(
            f"{path.name} contains multiple farm IDs."
        )

    matrix = np.asarray(
        [
            [
                float(row[feature])
                for feature in FEATURES
            ]
            for row in rows
        ],
        dtype=np.float32,
    )

    if matrix.size == 0:
        raise RuntimeError(
            f"{path.name} is empty."
        )

    if not np.isfinite(matrix).all():
        raise RuntimeError(
            f"{path.name} contains non-finite feature values."
        )

    return farm_ids[0], matrix


def make_sequences(matrix):
    X = []
    y = []

    last_origin = (
        len(matrix)
        - HORIZON_STEPS
    )

    for origin in range(
        HISTORY_STEPS,
        last_origin,
    ):

        history = matrix[
            origin - HISTORY_STEPS:
            origin
        ]

        target = matrix[
            origin + HORIZON_STEPS,
            FEATURES.index(TARGET),
        ]

        X.append(history)
        y.append(target)

    return (
        np.asarray(X, dtype=np.float32),
        np.asarray(y, dtype=np.float32),
    )


def standardize_train_only(
    X_train,
    y_train,
    X_val,
    y_val,
):

    # Feature-wise statistics from training data only.
    X_mean = X_train.reshape(-1, X_train.shape[-1]).mean(
        axis=0
    )

    X_std = X_train.reshape(-1, X_train.shape[-1]).std(
        axis=0
    )

    # Target statistics from training targets only.
    y_mean = y_train.mean()
    y_std = y_train.std()

    X_std = np.where(
        X_std < 1e-8,
        1.0,
        X_std,
    )

    if y_std < 1e-8:
        y_std = 1.0

    X_train_scaled = (
        X_train - X_mean
    ) / X_std

    X_val_scaled = (
        X_val - X_mean
    ) / X_std

    y_train_scaled = (
        y_train - y_mean
    ) / y_std

    y_val_scaled = (
        y_val - y_mean
    ) / y_std

    return (
        X_train_scaled.astype(np.float32),
        y_train_scaled.astype(np.float32),
        X_val_scaled.astype(np.float32),
        y_val_scaled.astype(np.float32),
        X_mean.astype(np.float64),
        X_std.astype(np.float64),
        float(y_mean),
        float(y_std),
    )


class MultivariateLSTM(nn.Module):

    def __init__(self):

        super().__init__()

        self.lstm = nn.LSTM(
            input_size=len(FEATURES),
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=(
                DROPOUT
                if NUM_LAYERS > 1
                else 0.0
            ),
        )

        self.output = nn.Linear(
            HIDDEN_SIZE,
            1,
        )

    def forward(self, x):

        output, _ = self.lstm(x)

        last_hidden = output[:, -1, :]

        return self.output(
            last_hidden
        ).squeeze(-1)


def train_model(
    X_train,
    y_train,
    X_val,
    y_val,
):

    model = MultivariateLSTM().to(DEVICE)

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    loss_function = nn.MSELoss()

    train_dataset = TensorDataset(
        torch.from_numpy(X_train),
        torch.from_numpy(y_train),
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    X_val_tensor = torch.from_numpy(
        X_val
    ).to(DEVICE)

    y_val_tensor = torch.from_numpy(
        y_val
    ).to(DEVICE)

    best_state = None
    best_val_loss = float("inf")
    best_epoch = 0
    epochs_without_improvement = 0

    start_time = time.time()

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        model.train()

        train_losses = []

        for X_batch, y_batch in train_loader:

            X_batch = X_batch.to(DEVICE)
            y_batch = y_batch.to(DEVICE)

            optimizer.zero_grad()

            predictions = model(
                X_batch
            )

            loss = loss_function(
                predictions,
                y_batch,
            )

            loss.backward()

            optimizer.step()

            train_losses.append(
                float(loss.item())
            )

        model.eval()

        with torch.no_grad():

            val_predictions = model(
                X_val_tensor
            )

            val_loss = float(
                loss_function(
                    val_predictions,
                    y_val_tensor,
                ).item()
            )

        train_loss = float(
            np.mean(train_losses)
        )

        improved = (
            val_loss
            <
            best_val_loss - 1e-10
        )

        if improved:

            best_val_loss = val_loss
            best_epoch = epoch

            best_state = {
                key: value.detach()
                .cpu()
                .clone()

                for key, value
                in model.state_dict().items()
            }

            epochs_without_improvement = 0

        else:

            epochs_without_improvement += 1

        elapsed = time.time() - start_time

        print(
            f"Epoch {epoch:02d}/{EPOCHS} | "
            f"train={train_loss:.6f} | "
            f"val={val_loss:.6f} | "
            f"best={best_val_loss:.6f} | "
            f"elapsed={int(elapsed)//60}m "
            f"{int(elapsed)%60:02d}s",
            flush=True,
        )

        if (
            epochs_without_improvement
            >= PATIENCE
        ):
            break

    if best_state is None:
        raise RuntimeError(
            "No valid checkpoint was created."
        )

    model.load_state_dict(
        best_state
    )

    return (
        model,
        best_epoch,
        best_val_loss,
        epoch,
    )


def evaluate_farm(path: Path):

    farm_id, matrix = read_farm(path)

    X, y = make_sequences(matrix)

    n = len(X)

    train_end = int(
        n * TRAIN_FRACTION
    )

    validation_end = int(
        n
        * (
            TRAIN_FRACTION
            + VALIDATION_FRACTION
        )
    )

    X_train = X[:train_end]
    y_train = y[:train_end]

    X_val = X[
        train_end:
        validation_end
    ]

    y_val = y[
        train_end:
        validation_end
    ]

    X_test = X[
        validation_end:
    ]

    y_test = y[
        validation_end:
    ]

    (
        X_train_scaled,
        y_train_scaled,
        X_val_scaled,
        y_val_scaled,
        X_mean,
        X_std,
        y_mean,
        y_std,
    ) = standardize_train_only(
        X_train,
        y_train,
        X_val,
        y_val,
    )

    X_test_scaled = (
        X_test - X_mean
    ) / X_std

    model, best_epoch, best_val_loss, epochs_run = train_model(
        X_train_scaled,
        y_train_scaled,
        X_val_scaled,
        y_val_scaled,
    )

    model.eval()

    X_test_tensor = torch.from_numpy(
        X_test_scaled.astype(np.float32)
    ).to(DEVICE)

    with torch.no_grad():

        scaled_predictions = (
            model(
                X_test_tensor
            )
            .cpu()
            .numpy()
            .astype(np.float64)
        )

    predictions = (
        scaled_predictions
        * y_std
        + y_mean
    )

    result_rmse = math.sqrt(
        float(
            np.mean(
                (
                    predictions
                    - y_test
                )
                ** 2
            )
        )
    )

    return {
        "farm_id": farm_id,
        "source_file": path.name,
        "total_rows": int(len(matrix)),
        "sequence_rows": int(n),
        "train_rows": int(len(X_train)),
        "validation_rows": int(len(X_val)),
        "test_rows": int(len(X_test)),
        "history_hours": 72,
        "horizon_hours": 72,
        "interval_minutes": 15,
        "history_steps": HISTORY_STEPS,
        "horizon_steps": HORIZON_STEPS,
        "metric": "DO RMSE (mg/L)",
        "features": FEATURES,
        "target": TARGET,
        "normalization": {
            "fit_on_training_only": True,
            "feature_means": X_mean.tolist(),
            "feature_stds": X_std.tolist(),
            "target_mean": y_mean,
            "target_std": y_std,
        },
        "model": {
            "architecture": "Multivariate LSTM",
            "input_size": len(FEATURES),
            "hidden_size": HIDDEN_SIZE,
            "layers": NUM_LAYERS,
            "dropout": DROPOUT,
            "batch_size": BATCH_SIZE,
            "epochs_requested": EPOCHS,
            "epochs_run": epochs_run,
            "best_epoch": best_epoch,
            "learning_rate": LEARNING_RATE,
            "random_seed": RANDOM_SEED,
            "optimizer": "Adam",
            "loss": "MSE",
            "patience": PATIENCE,
        },
        "rmse": result_rmse,
        "status": "INDEPENDENTLY_COMPUTED",
    }


results = [
    evaluate_farm(path)
    for path in FILES
]

total_test_rows = sum(
    result["test_rows"]
    for result in results
)

weighted_squared_error = sum(
    (
        result["rmse"] ** 2
    )
    * result["test_rows"]
    for result in results
)

fleet_rmse = math.sqrt(
    weighted_squared_error
    / total_test_rows
)


report = {
    "schema_version":
        "aqualife-v0110-lstm-task1-multivariate-v1",

    "generated_at_utc":
        now_utc(),

    "implementation":
        "AquaLife-owned multivariate LSTM baseline",

    "runtime": {
        "python":
            __import__("sys").version,

        "pytorch":
            torch.__version__,

        "device":
            str(DEVICE),
    },

    "data_scope": {
        "benchmark":
            "AquaSustain-Bench",

        "public_data":
            True,

        "commercial_data":
            False,

        "farms":
            ["A1", "B1", "C1"],
    },

    "task": {
        "id": 1,
        "name":
            "Water Quality Forecasting",
        "target":
            TARGET,
        "horizon_hours":
            72,
        "interval_minutes":
            15,
        "horizon_steps":
            HORIZON_STEPS,
        "primary_metric":
            "DO RMSE (mg/L)",
    },

    "protocol": {
        "history_hours":
            72,
        "history_steps":
            HISTORY_STEPS,
        "train_fraction":
            TRAIN_FRACTION,
        "validation_fraction":
            VALIDATION_FRACTION,
        "test_fraction":
            TEST_FRACTION,
        "chronological":
            True,
        "shuffle":
            False,
    },

    "features": FEATURES,

    "excluded_fields": [
        "disease_flag",
        "disease_category",
    ],

    "model": {
        "architecture":
            "Multivariate LSTM",
        "input_size":
            len(FEATURES),
        "hidden_size":
            HIDDEN_SIZE,
        "layers":
            NUM_LAYERS,
        "dropout":
            DROPOUT,
        "batch_size":
            BATCH_SIZE,
        "epochs":
            EPOCHS,
        "learning_rate":
            LEARNING_RATE,
        "optimizer":
            "Adam",
        "loss":
            "MSE",
        "random_seed":
            RANDOM_SEED,
    },

    "farms":
        results,

    "fleet": {
        "rmse":
            fleet_rmse,
        "test_rows":
            total_test_rows,
        "aggregation":
            "test-row weighted RMSE",
    },

    "scientific_boundary": {
        "independent_public_data_result":
            True,
        "real_world_validation":
            False,
        "production_accuracy_claim":
            False,
    },

    "safety": {
        "external_weights":
            False,
        "network":
            False,
        "automatic_training":
            False,
        "automatic_deployment":
            False,
    },

    "status":
        "PASS",
}


output = (
    OUTPUT
    / "task1-lstm-multivariate-report.json"
)

output.write_text(
    json.dumps(
        report,
        indent=2,
    ),
    encoding="utf-8",
)


print("=" * 72)
print("AquaLife Task-1 Multivariate LSTM")
print("=" * 72)

for result in results:

    print(
        f"{result['farm_id']} | "
        f"RMSE={result['rmse']:.6f} | "
        f"Best epoch={result['model']['best_epoch']}"
    )

print()
print(
    f"Fleet RMSE: {fleet_rmse:.6f}"
)

print()
print(
    f"Report: {output}"
)

print(
    "Multivariate LSTM computation: PASS"
)
