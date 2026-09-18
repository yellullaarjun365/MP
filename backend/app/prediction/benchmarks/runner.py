
from __future__ import annotations

from typing import Callable

from app.prediction.benchmarks.cases import (
    BenchmarkCase,
    BenchmarkResult,
)

from app.prediction.benchmarks.metrics import (
    regression_report,
)


def run_regression_benchmark(
    case: BenchmarkCase,
    model_id: str,
    actual: list[float],
    predicted: list[float],
) -> BenchmarkResult:

    if case.execution_required is False:

        notes = [
            "Benchmark executed using supplied predictions.",
            "No external model code was executed by the runner.",
        ]

    else:

        notes = [
            "Case requires an isolated execution environment."
        ]


    metrics = regression_report(
        actual,
        predicted,
    )


    return BenchmarkResult(

        benchmark_id=case.benchmark_id,

        model_id=model_id,

        status="PASS",

        metrics=metrics,

        observations=len(
            actual
        ),

        dataset_id=case.dataset_id,

        execution_status=(
            "PREDICTIONS_SUPPLIED"
        ),

        real_world_validated=(
            case.real_world
            and
            not case.synthetic
            and
            not case.aggregated
        ),

        production_approved=False,

        notes=notes,
    )
