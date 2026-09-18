from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.prediction.contracts.tasks import (
    FeatureContract,
)


class ModelAdapter(ABC):

    model_id: str

    task: str

    contract: FeatureContract


    @abstractmethod
    def predict(
        self,
        features: dict[str, Any],
    ) -> float | dict[str, Any]:

        raise NotImplementedError


    def validate_features(
        self,
        features: dict[str, Any],
    ) -> list[str]:

        required = {
            feature.name
            for feature in self.contract.features
            if feature.required
        }

        return sorted(
            required
            -
            set(features)
        )


    def health(
        self,
    ) -> dict[str, Any]:

        return {
            "model_id":
                self.model_id,

            "task":
                self.task,

            "status":
                "available",
        }
