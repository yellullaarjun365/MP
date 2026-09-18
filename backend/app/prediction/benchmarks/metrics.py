
from __future__ import annotations

import math


def validate_vectors(
    actual: list[float],
    predicted: list[float],
) -> None:

    if not actual:
        raise ValueError(
            "Actual vector is empty."
        )

    if len(actual) != len(
        predicted
    ):

        raise ValueError(
            "Actual/predicted lengths differ."
        )


def mae(
    actual: list[float],
    predicted: list[float],
) -> float:

    validate_vectors(
        actual,
        predicted,
    )

    return (
        sum(
            abs(
                a - p
            )
            for a, p
            in zip(
                actual,
                predicted,
            )
        )
        /
        len(actual)
    )


def mse(
    actual: list[float],
    predicted: list[float],
) -> float:

    validate_vectors(
        actual,
        predicted,
    )

    return (
        sum(
            (
                a - p
            ) ** 2
            for a, p
            in zip(
                actual,
                predicted,
            )
        )
        /
        len(actual)
    )


def rmse(
    actual: list[float],
    predicted: list[float],
) -> float:

    return math.sqrt(
        mse(
            actual,
            predicted,
        )
    )


def r2(
    actual: list[float],
    predicted: list[float],
) -> float | None:

    validate_vectors(
        actual,
        predicted,
    )

    mean_actual = (
        sum(actual)
        /
        len(actual)
    )

    ss_res = sum(
        (
            a - p
        ) ** 2
        for a, p
        in zip(
            actual,
            predicted,
        )
    )

    ss_tot = sum(
        (
            a - mean_actual
        ) ** 2
        for a
        in actual
    )

    if ss_tot == 0:
        return None

    return (
        1.0
        -
        (
            ss_res
            /
            ss_tot
        )
    )


def mape_pct(
    actual: list[float],
    predicted: list[float],
) -> float | None:

    validate_vectors(
        actual,
        predicted,
    )

    valid = [
        (
            a,
            p
        )
        for a, p
        in zip(
            actual,
            predicted,
        )
        if a != 0
    ]

    if not valid:
        return None

    return (
        sum(
            abs(
                (
                    a - p
                )
                /
                a
            )
            for a, p
            in valid
        )
        /
        len(valid)
        *
        100.0
    )


def regression_report(
    actual: list[float],
    predicted: list[float],
) -> dict[str, float | int | None]:

    return {
        "count": len(actual),
        "mae": mae(
            actual,
            predicted,
        ),
        "mse": mse(
            actual,
            predicted,
        ),
        "rmse": rmse(
            actual,
            predicted,
        ),
        "r2": r2(
            actual,
            predicted,
        ),
        "mape_pct": mape_pct(
            actual,
            predicted,
        ),
    }
