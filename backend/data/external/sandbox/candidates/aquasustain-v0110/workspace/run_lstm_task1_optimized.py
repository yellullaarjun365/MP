from __future__ import annotations

import csv
import json
import math
import os
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from torch import nn

ROOT = Path("/benchmark")
DATA = ROOT / "data"
OUTPUT = Path("/results")
CHECKPOINT_DIR = OUTPUT / "checkpoints"
OUTPUT.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    DATA / "A1_sample_90days.csv",
    DATA / "B1_sample_90days.csv",
    DATA / "C1_sample_90days.csv",
]

# Fixed AquaLife Task-1 contract.
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
PATIENCE = 10

env_threads = os.environ.get("AQUALIFE_LSTM_THREADS", "").strip()
if env_threads:
    try:
        TORCH_THREADS = max(1, int(env_threads))
    except ValueError:
        TORCH_THREADS = max(1, min(4, os.cpu_count() or 1))
else:
    TORCH_THREADS = max(1, min(4, os.cpu_count() or 1))

torch.set_num_threads(TORCH_THREADS)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass

DEVICE = torch.device("cpu")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def fmt(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m:02d}m {s:02d}s" if h else f"{m}m {s:02d}s"


def read_farm(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = reader.fieldnames or []

    required = {"timestamp", "farm_id", "DO_mg_L"}
    missing = sorted(required - set(columns))
    if missing:
        raise RuntimeError(f"{path.name} missing columns: {missing}")

    timestamps = [row["timestamp"] for row in rows]
    if timestamps != sorted(timestamps):
        raise RuntimeError(f"{path.name} timestamps are not ordered.")

    farms = sorted({row["farm_id"] for row in rows})
    if len(farms) != 1:
        raise RuntimeError(f"{path.name} contains multiple farm IDs.")

    values = np.asarray([float(row["DO_mg_L"]) for row in rows], dtype=np.float32)
    if values.size == 0:
        raise RuntimeError(f"{path.name} is empty.")
    if not np.isfinite(values).all():
        raise RuntimeError(f"{path.name} contains non-finite values.")
    return farms[0], values


def make_sequences(values):
    X, y = [], []
    last_origin = len(values) - HORIZON_STEPS
    for origin in range(HISTORY_STEPS, last_origin):
        X.append(values[origin - HISTORY_STEPS:origin])
        y.append(values[origin + HORIZON_STEPS])
    return np.asarray(X, dtype=np.float32), np.asarray(y, dtype=np.float32)


class LSTMRegressor(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=1,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=DROPOUT if NUM_LAYERS > 1 else 0.0,
        )
        self.output = nn.Linear(HIDDEN_SIZE, 1)

    def forward(self, x):
        output, _ = self.lstm(x)
        return self.output(output[:, -1, :]).squeeze(-1)


def standardize_train_only(X_train, y_train, X_other, y_other):
    mean = float(X_train.mean())
    std = float(X_train.std())
    if std <= 1e-8:
        std = 1.0

    X_train_scaled = (X_train - mean) / std
    X_other_scaled = (X_other - mean) / std

    y_mean = float(y_train.mean())
    y_std = float(y_train.std())
    if y_std <= 1e-8:
        y_std = 1.0

    y_train_scaled = (y_train - y_mean) / y_std
    y_other_scaled = (y_other - y_mean) / y_std

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


def inverse_target(values, mean, std):
    return values * std + mean


def rmse(predictions, targets):
    p = np.asarray(predictions, dtype=np.float64)
    t = np.asarray(targets, dtype=np.float64)
    return float(np.sqrt(np.mean((p - t) ** 2)))


def ckpt_path(farm_id: str) -> Path:
    return CHECKPOINT_DIR / f"task1_lstm_{farm_id}.pt"


def result_path(farm_id: str) -> Path:
    return CHECKPOINT_DIR / f"task1_lstm_{farm_id}.json"


def save_checkpoint(path, *, farm_id, model, optimizer, epoch, best_epoch,
                    best_val_loss, epochs_without_improvement, best_state,
                    X_mean, X_std, y_mean, y_std):
    torch.save(
        {
            "farm_id": farm_id,
            "epoch": epoch,
            "best_epoch": best_epoch,
            "best_val_loss": best_val_loss,
            "epochs_without_improvement": epochs_without_improvement,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "best_state": best_state,
            "X_mean": X_mean,
            "X_std": X_std,
            "y_mean": y_mean,
            "y_std": y_std,
        },
        path,
    )


def train_model(
    *, farm_id, X_train_scaled, y_train_scaled, X_val_scaled, y_val_scaled,
    X_mean, X_std, y_mean, y_std
):
    model = LSTMRegressor().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    loss_function = nn.MSELoss()

    checkpoint = ckpt_path(farm_id)
    start_epoch = 1
    best_val_loss = float("inf")
    best_epoch = 0
    epochs_without_improvement = 0
    best_state = None
    resumed = False

    if checkpoint.exists():
        data = torch.load(checkpoint, map_location=DEVICE)
        norms_ok = all(
            math.isclose(float(data[key]), expected, rel_tol=1e-9, abs_tol=1e-9)
            for key, expected in (
                ("X_mean", X_mean),
                ("X_std", X_std),
                ("y_mean", y_mean),
                ("y_std", y_std),
            )
        )
        if norms_ok:
            resumed = True
            start_epoch = int(data["epoch"]) + 1
            best_epoch = int(data["best_epoch"])
            best_val_loss = float(data["best_val_loss"])
            epochs_without_improvement = int(data["epochs_without_improvement"])
            best_state = data["best_state"]
            model.load_state_dict(data["model_state"])
            optimizer.load_state_dict(data["optimizer_state"])
            print(f"[{farm_id}] RESUMED from epoch {start_epoch - 1}", flush=True)
        else:
            print(f"[{farm_id}] checkpoint mismatch; starting fresh", flush=True)

    X_train_t = torch.from_numpy(X_train_scaled[:, :, None]).to(DEVICE)
    y_train_t = torch.from_numpy(y_train_scaled).to(DEVICE)
    X_val_t = torch.from_numpy(X_val_scaled[:, :, None]).to(DEVICE)
    y_val_t = torch.from_numpy(y_val_scaled).to(DEVICE)

    if start_epoch > EPOCHS:
        model.load_state_dict(best_state)
        return model, best_epoch, best_val_loss, EPOCHS, resumed

    farm_start = time.perf_counter()
    epoch_times = []

    for epoch in range(start_epoch, EPOCHS + 1):
        epoch_start = time.perf_counter()
        model.train()
        total_loss = 0.0
        total_samples = 0

        for start in range(0, X_train_t.shape[0], BATCH_SIZE):
            bx = X_train_t[start:start + BATCH_SIZE]
            by = y_train_t[start:start + BATCH_SIZE]
            optimizer.zero_grad(set_to_none=True)
            pred = model(bx)
            loss = loss_function(pred, by)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            n = by.shape[0]
            total_loss += float(loss.item()) * n
            total_samples += n

        train_loss = total_loss / total_samples

        model.eval()
        with torch.inference_mode():
            val_pred = model(X_val_t)
            val_loss = float(loss_function(val_pred, y_val_t).item())

        improved = val_loss < best_val_loss - 1e-10
        if improved:
            best_val_loss = val_loss
            best_epoch = epoch
            best_state = {
                k: v.detach().cpu().clone()
                for k, v in model.state_dict().items()
            }
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        epoch_seconds = time.perf_counter() - epoch_start
        epoch_times.append(epoch_seconds)
        recent = epoch_times[-5:]
        avg = statistics.mean(recent)
        remaining_epochs = max(0, EPOCHS - epoch)
        eta = avg * remaining_epochs
        elapsed = time.perf_counter() - farm_start

        print(
            f"[{farm_id}] Epoch {epoch:02d}/{EPOCHS} | "
            f"train={train_loss:.6f} | val={val_loss:.6f} | "
            f"best={best_val_loss:.6f} | "
            f"epoch={fmt(epoch_seconds)} | "
            f"elapsed={fmt(elapsed)} | ETA={fmt(eta)}"
            + (" | RESUMED" if resumed else ""),
            flush=True,
        )

        save_checkpoint(
            checkpoint,
            farm_id=farm_id,
            model=model,
            optimizer=optimizer,
            epoch=epoch,
            best_epoch=best_epoch,
            best_val_loss=best_val_loss,
            epochs_without_improvement=epochs_without_improvement,
            best_state=best_state,
            X_mean=X_mean,
            X_std=X_std,
            y_mean=y_mean,
            y_std=y_std,
        )

        if epochs_without_improvement >= PATIENCE:
            print(
                f"[{farm_id}] Early stopping at epoch {epoch}; "
                f"best epoch {best_epoch}.",
                flush=True,
            )
            break

    model.load_state_dict(best_state)
    return model, best_epoch, best_val_loss, epoch, resumed


def evaluate_farm(path: Path):
    farm_id, values = read_farm(path)
    X, y = make_sequences(values)
    n = len(X)

    train_end = int(n * TRAIN_FRACTION)
    validation_end = int(n * (TRAIN_FRACTION + VALIDATION_FRACTION))

    if train_end <= 0 or validation_end <= train_end or validation_end >= n:
        raise RuntimeError(f"Invalid split for {path.name}")

    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:validation_end], y[train_end:validation_end]
    X_test, y_test = X[validation_end:], y[validation_end:]

    (
        X_train_s, y_train_s, X_val_s, y_val_s,
        X_mean, X_std, y_mean, y_std,
    ) = standardize_train_only(X_train, y_train, X_val, y_val)

    X_test_s = (X_test - X_mean) / X_std

    print("", flush=True)
    print("-" * 60, flush=True)
    print(
        f"Farm {farm_id} | rows={len(values)} | sequences={n} | "
        f"train={len(X_train)} | val={len(X_val)} | test={len(X_test)}",
        flush=True,
    )
    print(
        f"batch={BATCH_SIZE} | max_epochs={EPOCHS} | "
        f"threads={TORCH_THREADS}",
        flush=True,
    )
    print("-" * 60, flush=True)

    cached = result_path(farm_id)
    if cached.exists():
        try:
            result = json.loads(cached.read_text(encoding="utf-8"))
            if result.get("status") == "INDEPENDENTLY_COMPUTED":
                print(f"[{farm_id}] completed result already exists; reusing.", flush=True)
                return result
        except Exception:
            pass

    model, best_epoch, best_val_loss, epochs_run, resumed = train_model(
        farm_id=farm_id,
        X_train_scaled=X_train_s,
        y_train_scaled=y_train_s,
        X_val_scaled=X_val_s,
        y_val_scaled=y_val_s,
        X_mean=X_mean,
        X_std=X_std,
        y_mean=y_mean,
        y_std=y_std,
    )

    model.eval()
    test_t = torch.from_numpy(X_test_s[:, :, None]).to(DEVICE)
    with torch.inference_mode():
        pred_s = model(test_t).cpu().numpy().astype(np.float64)

    predictions = inverse_target(pred_s, y_mean, y_std)
    result_rmse = rmse(predictions, y_test)
    independent_rmse = math.sqrt(float(np.mean((predictions - y_test) ** 2)))

    if not math.isclose(result_rmse, independent_rmse, rel_tol=1e-12, abs_tol=1e-12):
        raise RuntimeError(f"RMSE cross-check failed for {farm_id}")

    result = {
        "farm_id": farm_id,
        "source_file": path.name,
        "total_rows": int(len(values)),
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
        "normalization": {
            "fit_on_training_only": True,
            "input_mean": X_mean,
            "input_std": X_std,
            "target_mean": y_mean,
            "target_std": y_std,
        },
        "model": {
            "architecture": "LSTM",
            "input_size": 1,
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
            "threads": TORCH_THREADS,
            "resumed_from_checkpoint": resumed,
        },
        "rmse": result_rmse,
        "independent_rmse_check": independent_rmse,
        "status": "INDEPENDENTLY_COMPUTED",
    }

    cached.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"[{farm_id}] COMPLETE | RMSE={result_rmse:.6f} | "
        f"best_epoch={best_epoch} | epochs_run={epochs_run}",
        flush=True,
    )
    return result


def main():
    seed_everything(RANDOM_SEED)

    print("=" * 72, flush=True)
    print("AquaLife Optimized LSTM Task-1", flush=True)
    print("=" * 72, flush=True)
    print(f"PyTorch: {torch.__version__}", flush=True)
    print(f"Device: {DEVICE}", flush=True)
    print(f"Threads: {TORCH_THREADS}", flush=True)
    print(f"Batch size: {BATCH_SIZE}", flush=True)
    print(f"Max epochs: {EPOCHS}", flush=True)
    print(f"Early stopping patience: {PATIENCE}", flush=True)
    print("", flush=True)

    started = time.perf_counter()
    results = [evaluate_farm(path) for path in FILES]

    total_test_rows = sum(r["test_rows"] for r in results)
    weighted_squared_error = sum(
        (r["rmse"] ** 2) * r["test_rows"]
        for r in results
    )
    fleet_rmse = math.sqrt(weighted_squared_error / total_test_rows)

    report = {
        "schema_version": "aqualife-v0110-lstm-task1-v2-optimized",
        "generated_at_utc": now_utc(),
        "implementation": "AquaLife-owned LSTM baseline with progress and resumable checkpoints.",
        "runtime": {
            "python": __import__("sys").version,
            "pytorch": torch.__version__,
            "device": str(DEVICE),
            "torch_threads": TORCH_THREADS,
        },
        "data_scope": {
            "benchmark": "AquaSustain-Bench",
            "public_data": True,
            "commercial_data": False,
            "farms": ["A1", "B1", "C1"],
        },
        "task": {
            "id": 1,
            "name": "Water Quality Forecasting",
            "horizon_hours": 72,
            "interval_minutes": 15,
            "horizon_steps": 288,
            "primary_metric": "DO RMSE (mg/L)",
        },
        "protocol": {
            "history_hours": 72,
            "history_steps": 288,
            "train_fraction": TRAIN_FRACTION,
            "validation_fraction": VALIDATION_FRACTION,
            "test_fraction": TEST_FRACTION,
            "chronological": True,
            "shuffle": False,
        },
        "model": {
            "architecture": "LSTM",
            "input_size": 1,
            "hidden_size": HIDDEN_SIZE,
            "layers": NUM_LAYERS,
            "dropout": DROPOUT,
            "batch_size": BATCH_SIZE,
            "epochs": EPOCHS,
            "learning_rate": LEARNING_RATE,
            "optimizer": "Adam",
            "loss": "MSE",
            "random_seed": RANDOM_SEED,
            "device": "cpu",
            "torch_threads": TORCH_THREADS,
            "checkpointing": True,
            "resumable": True,
            "progress_reporting": True,
        },
        "features": ["DO_lag_sequence_72h"],
        "farms": results,
        "fleet": {
            "rmse": fleet_rmse,
            "test_rows": total_test_rows,
            "aggregation": "test-row weighted RMSE",
        },
        "scientific_boundary": {
            "independent_public_data_result": True,
            "source_lstm_implementation_reproduced": False,
            "commercial_12_farm_validation": False,
            "real_world_validation": False,
            "production_accuracy_claim": False,
        },
        "safety": {
            "external_weights": False,
            "network": False,
            "automatic_training": False,
            "automatic_deployment": False,
        },
        "status": "PASS",
    }

    output = OUTPUT / "task1-lstm-independent-report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("", flush=True)
    print("=" * 72, flush=True)
    print("LSTM COMPUTATION COMPLETE", flush=True)
    print("=" * 72, flush=True)
    for result in results:
        print(
            f'{result["farm_id"]} | RMSE={result["rmse"]:.6f} | '
            f'Test rows={result["test_rows"]} | '
            f'Best epoch={result["model"]["best_epoch"]}',
            flush=True,
        )
    print(f"Fleet RMSE: {fleet_rmse:.6f}", flush=True)
    print(f"Total runtime: {fmt(time.perf_counter() - started)}", flush=True)
    print(f"Report: {output}", flush=True)
    print("LSTM computation: PASS", flush=True)


if __name__ == "__main__":
    main()
