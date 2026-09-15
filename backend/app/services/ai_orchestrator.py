from typing import Any

from app.services.context_intent_service import (
    classify_intent,
)
from app.services.parameter_extraction_engine import (
    extract_normalize_validate,
)


def process_aquaculture_message(
    text: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:

    history = history or []

    intent = classify_intent(
        text=text,
        history=history,
    )

    result: dict[str, Any] = {
        "intent": intent.intent,
        "confidence": intent.confidence,
        "reason": intent.reason,
        "parameters": None,
        "missing_fields": [],
        "ambiguities": [],
        "validation_warnings": [],
    }

    if intent.intent in {
        "farm_data",
        "parameter_update",
    }:

        extracted = extract_normalize_validate(
            text
        )

        result.update(
            {
                "parameters": extracted["parameters"],
                "missing_fields": extracted["missing_fields"],
                "ambiguities": extracted["ambiguities"],
                "validation_warnings": extracted[
                    "validation_warnings"
                ],
            }
        )

    return result


if __name__ == "__main__":

    history = [
        {
            "role": "user",
            "content": "My farm grows Vannamei shrimp.",
        },
        {
            "role": "user",
            "content": "My survival rate is 82 percent.",
        },
    ]

    tests = [
        "Actually my survival is 85 percent.",
        (
            "My pond is 2 acres and I stocked "
            "20000 Vannamei. Average weight is 18 grams."
        ),
        "What is dissolved oxygen?",
        "Predict my production.",
    ]

    for text in tests:

        print("\n================================")
        print("INPUT:")
        print(text)

        result = process_aquaculture_message(
            text=text,
            history=history,
        )

        print("\nRESULT:")
        print(result)
