from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


@dataclass(frozen=True)
class RegressionMetrics:

    mae: float
    rmse: float
    r2: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def evaluate_regression(
    y_true,
    y_pred,
) -> RegressionMetrics:

    rmse = float(
        np.sqrt(
            mean_squared_error(
                y_true,
                y_pred,
            )
        )
    )

    return RegressionMetrics(
        mae=float(
            mean_absolute_error(
                y_true,
                y_pred,
            )
        ),
        rmse=rmse,
        r2=float(
            r2_score(
                y_true,
                y_pred,
            )
        ),
    )
