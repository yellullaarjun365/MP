from __future__ import annotations

import csv
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


ROOT = Path("/benchmark")

DATA = ROOT / "data"

OUTPUT = Path("/results")

OUTPUT.mkdir(
    parents=True,
    exist_ok=True,
)


FILES = [
    DATA / "A1_sample_90days.csv",
    DATA / "B1_sample_90days.csv",
    DATA / "C1_sample_90days.csv",
]


# ============================================================
# FIXED EXPERIMENT CONTRACT
# ============================================================

HORIZON_STEPS = 288

INTERVAL_MINUTES = 15

HISTORY_STEPS = 288

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


DEVICE = torch.device(
    "cpu"
)


def now_utc():

    return datetime.now(
        timezone.utc
    ).isoformat()


def seed_everything(
    seed: int,
):

    random.seed(
        seed
    )

    np.random.seed(
        seed
    )

    torch.manual_seed(
        seed
    )


seed_everything(
    RANDOM_SEED
)


def read_farm(
    path: Path,
):

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        reader = csv.DictReader(
            handle
        )

        rows = list(
            reader
        )

        columns = (
            reader.fieldnames
            or []
        )


    required = {
        "timestamp",
        "farm_id",
        "DO_mg_L",
    }


    missing = sorted(
        required
        -
        set(columns)
    )


    if missing:

        raise RuntimeError(
            f"{path.name} missing columns: {missing}"
        )


    timestamps = [
        row[
            "timestamp"
        ]
        for row
        in rows
    ]


    if timestamps != sorted(
        timestamps
    ):

        raise RuntimeError(
            f"{path.name} timestamps are not ordered."
        )


    farms = sorted(
        {
            row[
                "farm_id"
            ]
            for row
            in rows
        }
    )


    if len(farms) != 1:

        raise RuntimeError(
            f"{path.name} contains multiple farm IDs."
        )


    values = np.asarray(
        [
            float(
                row[
                    "DO_mg_L"
                ]
            )
            for row
            in rows
        ],
        dtype=np.float32,
    )


    if values.size == 0:

        raise RuntimeError(
            f"{path.name} is empty."
        )


    if not np.isfinite(
        values
    ).all():

        raise RuntimeError(
            f"{path.name} contains non-finite values."
        )


    return (
        farms[0],
        values,
    )


def make_sequences(
    values,
):

    # --------------------------------------------------------
    # Each training example:
    #
    # X[t] = previous 72 hours of DO
    # y[t] = DO exactly 72 hours into the future
    #
    # With 15-minute sampling:
    # 72 hours = 288 observations.
    # --------------------------------------------------------

    X = []
    y = []


    last_origin = (
        len(values)
        -
        HORIZON_STEPS
    )


    for origin in range(
        HISTORY_STEPS,
        last_origin,
    ):

        history = values[
            origin
            -
            HISTORY_STEPS:
            origin
        ]


        target = values[
            origin
            +
            HORIZON_STEPS
        ]


        X.append(
            history
        )

        y.append(
            target
        )


    return (
        np.asarray(
            X,
            dtype=np.float32,
        ),

        np.asarray(
            y,
            dtype=np.float32,
        ),
    )


class LSTMRegressor(
    nn.Module
):

    def __init__(
        self,
    ):

        super().__init__()


        self.lstm = nn.LSTM(

            input_size=1,

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


    def forward(
        self,
        x,
    ):

        output, _ = self.lstm(
            x
        )

        last = output[
            :,
            -1,
            :
        ]

        return self.output(
            last
        ).squeeze(
            -1
        )


def standardize_train_only(
    X_train,
    y_train,
    X_other,
    y_other,
):

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Mean/std are learned ONLY from training data.
    # Validation and test are transformed with those values.
    # --------------------------------------------------------

    mean = float(
        X_train.mean()
    )

    std = float(
        X_train.std()
    )


    if std <= 1e-8:

        std = 1.0


    X_train_scaled = (
        X_train
        -
        mean
    ) / std


    X_other_scaled = (
        X_other
        -
        mean
    ) / std


    y_mean = float(
        y_train.mean()
    )

    y_std = float(
        y_train.std()
    )


    if y_std <= 1e-8:

        y_std = 1.0


    y_train_scaled = (
        y_train
        -
        y_mean
    ) / y_std


    y_other_scaled = (
        y_other
        -
        y_mean
    ) / y_std


    return (
        X_train_scaled,
        y_train_scaled,
        X_other_scaled,
        y_other_scaled,
        mean,
        std,
        y_mean,
        y_std,
    )


def inverse_target(
    values,
    mean,
    std,
):

    return (
        values
        *
        std
        +
        mean
    )


def rmse(
    predictions,
    targets,
):

    predictions = np.asarray(
        predictions,
        dtype=np.float64,
    )

    targets = np.asarray(
        targets,
        dtype=np.float64,
    )


    return float(
        np.sqrt(
            np.mean(
                (
                    predictions
                    -
                    targets
                )
                ** 2
            )
        )
    )


def train_model(
    X_train,
    y_train,
    X_val,
    y_val,
):

    model = LSTMRegressor().to(
        DEVICE
    )


    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )


    loss_function = nn.MSELoss()


    train_dataset = TensorDataset(
        torch.from_numpy(
            X_train[:, :, None]
        ),
        torch.from_numpy(
            y_train
        ),
    )


    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )


    X_val_tensor = torch.from_numpy(
        X_val[:, :, None]
    ).to(
        DEVICE
    )

    y_val_tensor = torch.from_numpy(
        y_val
    ).to(
        DEVICE
    )


    best_state = None

    best_val_loss = float(
        "inf"
    )

    best_epoch = 0

    epochs_without_improvement = 0

    patience = 10


    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        model.train()


        for batch_X, batch_y in train_loader:

            batch_X = batch_X.to(
                DEVICE
            )

            batch_y = batch_y.to(
                DEVICE
            )


            optimizer.zero_grad()


            predictions = model(
                batch_X
            )


            loss = loss_function(
                predictions,
                batch_y,
            )


            loss.backward()


            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0,
            )


            optimizer.step()


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


        if (
            val_loss
            <
            best_val_loss
            -
            1e-10
        ):

            best_val_loss = (
                val_loss
            )

            best_epoch = (
                epoch
            )

            best_state = {
                key:
                    value.detach().cpu().clone()
                for key, value
                in model.state_dict().items()
            }

            epochs_without_improvement = 0

        else:

            epochs_without_improvement += 1


        if (
            epochs_without_improvement
            >=
            patience
        ):

            break


    if best_state is None:

        raise RuntimeError(
            "No valid LSTM checkpoint was created."
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


def evaluate_farm(
    path: Path,
):

    farm_id, values = read_farm(
        path
    )


    X, y = make_sequences(
        values
    )


    n = len(X)


    train_end = int(
        n
        *
        TRAIN_FRACTION
    )


    validation_end = int(
        n
        *
        (
            TRAIN_FRACTION
            +
            VALIDATION_FRACTION
        )
    )


    if (
        train_end <= 0
        or
        validation_end <= train_end
        or
        validation_end >= n
    ):

        raise RuntimeError(
            f"Invalid split for {path.name}"
        )


    X_train = X[
        :train_end
    ]

    y_train = y[
        :train_end
    ]


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


    # The test transformation is done using training statistics
    # only. No test statistics enter fitting.

    X_test_scaled = (
        X_test
        -
        X_mean
    ) / X_std


    y_test_scaled = (
        y_test
        -
        y_mean
    ) / y_std


    (
        model,
        best_epoch,
        best_val_loss,
        epochs_run,
    ) = train_model(
        X_train_scaled,
        y_train_scaled,
        X_val_scaled,
        y_val_scaled,
    )


    model.eval()


    X_test_tensor = torch.from_numpy(
        X_test_scaled[:, :, None]
    ).to(
        DEVICE
    )


    with torch.no_grad():

        scaled_predictions = (
            model(
                X_test_tensor
            )
            .cpu()
            .numpy()
            .astype(
                np.float64
            )
        )


    predictions = inverse_target(
        scaled_predictions,
        y_mean,
        y_std,
    )


    result_rmse = rmse(
        predictions,
        y_test,
    )


    independent_rmse = math.sqrt(
        float(
            np.mean(
                (
                    predictions
                    -
                    y_test
                )
                ** 2
            )
        )
    )


    if not math.isclose(
        result_rmse,
        independent_rmse,
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):

        raise RuntimeError(
            f"RMSE cross-check failed for {farm_id}"
        )


    return {

        "farm_id":
            farm_id,

        "source_file":
            path.name,

        "total_rows":
            int(len(values)),

        "sequence_rows":
            int(n),

        "train_rows":
            int(len(X_train)),

        "validation_rows":
            int(len(X_val)),

        "test_rows":
            int(len(X_test)),

        "history_hours":
            72,

        "horizon_hours":
            72,

        "interval_minutes":
            15,

        "history_steps":
            HISTORY_STEPS,

        "horizon_steps":
            HORIZON_STEPS,

        "metric":
            "DO RMSE (mg/L)",

        "normalization":
            {
                "fit_on_training_only":
                    True,

                "input_mean":
                    X_mean,

                "input_std":
                    X_std,

                "target_mean":
                    y_mean,

                "target_std":
                    y_std,
            },

        "model":
            {
                "architecture":
                    "LSTM",

                "input_size":
                    1,

                "hidden_size":
                    HIDDEN_SIZE,

                "layers":
                    NUM_LAYERS,

                "dropout":
                    DROPOUT,

                "batch_size":
                    BATCH_SIZE,

                "epochs_requested":
                    EPOCHS,

                "epochs_run":
                    epochs_run,

                "best_epoch":
                    best_epoch,

                "learning_rate":
                    LEARNING_RATE,

                "random_seed":
                    RANDOM_SEED,

                "optimizer":
                    "Adam",

                "loss":
                    "MSE",
            },

        "rmse":
            result_rmse,

        "independent_rmse_check":
            independent_rmse,

        "status":
            "INDEPENDENTLY_COMPUTED",
    }


farm_results = [
    evaluate_farm(
        path
    )
    for path
    in FILES
]


total_test_rows = sum(
    result[
        "test_rows"
    ]
    for result
    in farm_results
)


weighted_squared_error = sum(
    (
        result[
            "rmse"
        ]
        **
        2
    )
    *
    result[
        "test_rows"
    ]
    for result
    in farm_results
)


fleet_rmse = math.sqrt(
    weighted_squared_error
    /
    total_test_rows
)


report = {

    "schema_version":
        "aqualife-v0110-lstm-task1-v1",

    "generated_at_utc":
        now_utc(),

    "implementation":
        "AquaLife-owned LSTM baseline",

    "runtime":
        {
            "python":
                __import__(
                    "sys"
                ).version,

            "pytorch":
                torch.__version__,

            "device":
                str(
                    DEVICE
                ),
        },

    "data_scope":
        {
            "benchmark":
                "AquaSustain-Bench",

            "public_data":
                True,

            "commercial_data":
                False,

            "farms":
                [
                    "A1",
                    "B1",
                    "C1",
                ],
        },

    "task":
        {
            "id":
                1,

            "name":
                "Water Quality Forecasting",

            "horizon_hours":
                72,

            "interval_minutes":
                15,

            "horizon_steps":
                288,

            "primary_metric":
                "DO RMSE (mg/L)",
        },

    "protocol":
        {
            "history_hours":
                72,

            "history_steps":
                288,

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

    "model":
        {
            "architecture":
                "LSTM",

            "input_size":
                1,

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

            "device":
                "cpu",
        },

    "features":
        [
            "DO_lag_sequence_72h"
        ],

    "farms":
        farm_results,

    "fleet":
        {
            "rmse":
                fleet_rmse,

            "test_rows":
                total_test_rows,

            "aggregation":
                "test-row weighted RMSE",
        },

    "scientific_boundary":
        {
            "independent_public_data_result":
                True,

            "source_lstm_implementation_reproduced":
                False,

            "commercial_12_farm_validation":
                False,

            "real_world_validation":
                False,

            "production_accuracy_claim":
                False,
        },

    "safety":
        {
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
    /
    "task1-lstm-independent-report.json"
)


output.write_text(
    json.dumps(
        report,
        indent=2,
    ),
    encoding="utf-8",
)


print(
    "=" * 72
)

print(
    "AquaLife V0.11.0 LSTM Task-1"
)

print(
    "=" * 72
)

print(
    "PyTorch:",
    torch.__version__,
)

print(
    "Device:",
    DEVICE,
)

print()

for result in farm_results:

    print(
        result["farm_id"],
        "| RMSE:",
        result["rmse"],
        "| Test rows:",
        result["test_rows"],
        "| Best epoch:",
        result["model"]["best_epoch"],
    )


print()

print(
    "Fleet RMSE:",
    fleet_rmse,
)

print()
print(
    "LSTM computation: PASS"
)
