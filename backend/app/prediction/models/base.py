from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProductionModel(ABC):

    name: str = "unknown"
    version: str = "unknown"

    @abstractmethod
    def fit(
        self,
        X: Any,
        y: Any,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(
        self,
        X: Any,
    ) -> Any:
        raise NotImplementedError

    def predict_interval(
        self,
        X: Any,
    ) -> tuple[Any, Any]:

        raise NotImplementedError(
            "This model does not provide "
            "prediction intervals."
        )
