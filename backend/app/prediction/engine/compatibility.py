from __future__ import annotations

from typing import Any

from app.prediction.contracts.registry import (
    get_contract,
)

from app.prediction.contracts.tasks import (
    CompatibilityResult,
)


def check_compatibility(
    task: str,
    model_id: str,
    input_features: dict[str, Any],
    model_features: list[str] | None = None,
) -> CompatibilityResult:

    contract = get_contract(
        task
    )


    contract_features = {
        feature.name
        for feature in contract.features
    }


    required_features = {
        feature.name
        for feature in contract.features
        if feature.required
    }


    provided = set(
        input_features
    )


    missing = sorted(
        required_features
        -
        provided
    )


    extra = sorted(
        provided
        -
        contract_features
    )


    incompatible: list[str] = []

    reasons: list[str] = []


    if missing:

        reasons.append(
            "Required contract features are missing."
        )


    if model_features is not None:

        model_required = set(
            model_features
        )

        model_missing = sorted(
            model_required
            -
            provided
        )

        incompatible.extend(
            model_missing
        )

        if model_missing:

            reasons.append(
                "Model-specific features are missing."
            )


    compatible = (
        len(missing) == 0
        and
        len(incompatible) == 0
    )


    denominator = max(
        len(required_features),
        1,
    )


    available = (
        len(required_features)
        -
        len(missing)
    )


    score = (
        available
        /
        denominator
    )


    if compatible:

        reasons.append(
            "All required features are present."
        )


    return CompatibilityResult(
        compatible=compatible,

        task=task,

        model_id=model_id,

        missing_features=missing,

        extra_features=extra,

        incompatible_features=sorted(
            set(incompatible)
        ),

        reasons=reasons,

        score=round(
            score,
            4,
        ),

        metadata={
            "contract_id":
                contract.contract_id,

            "target":
                contract.target,

            "granularity":
                contract.granularity,
        },
    )
