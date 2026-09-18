from __future__ import annotations

from typing import Any

from app.prediction.adapters.base import (
    ModelAdapter,
)

from app.prediction.contracts.registry import (
    POND_PRODUCTION_CONTRACT,
)


class CatBoostProductionAdapter(
    ModelAdapter
):

    model_id = (
        "aqualife-catboost-production-v0.2"
    )

    task = (
        "pond_production_regression"
    )

    contract = (
        POND_PRODUCTION_CONTRACT
    )


    def predict(
        self,
        features: dict[str, Any],
    ) -> float:

        missing = self.validate_features(
            features
        )

        if missing:

            raise ValueError(
                "Missing model features: "
                + ", ".join(missing)
            )

        from app.prediction.models.catboost import (
            predict,
        )

        return float(
            predict(
                features
            )
        )
