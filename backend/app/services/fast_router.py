from app.services.context_intent_service import classify_intent


PARAMETER_HINTS = [
    "my pond",
    "my farm",
    "my stocking",
    "my survival",
    "my temperature",
    "my ph",
    "my dissolved oxygen",
    "my oxygen",
    "my salinity",
    "my feed",
    "my average weight",
    "i stocked",
    "i have a pond",
    "i farm",
    "i grow",
    "our pond",
    "our farm",
]


UPDATE_HINTS = [
    "actually",
    "update",
    "updated",
    "change",
    "changed",
    "correct",
    "correction",
    "instead",
    "now it is",
    "now it's",
]


PREDICTION_HINTS = [
    "predict",
    "prediction",
    "forecast",
    "forecasting",
    "estimate production",
    "expected production",
    "expected harvest",
]


KNOWLEDGE_HINTS = [
    "what is",
    "why is",
    "why does",
    "how does",
    "how do",
    "explain",
    "define",
    "tell me about",
]


def contains_any(
    text: str,
    hints: list[str],
) -> bool:

    value = text.lower().strip()

    return any(
        hint in value
        for hint in hints
    )


def looks_like_parameter_message(
    text: str,
) -> bool:

    return contains_any(
        text,
        PARAMETER_HINTS,
    )


def looks_like_update(
    text: str,
) -> bool:

    return contains_any(
        text,
        UPDATE_HINTS,
    )


def looks_like_prediction(
    text: str,
) -> bool:

    return contains_any(
        text,
        PREDICTION_HINTS,
    )


def looks_like_knowledge(
    text: str,
) -> bool:

    return contains_any(
        text,
        KNOWLEDGE_HINTS,
    )


def route_message(
    text: str,
    history: list[dict[str, str]] | None = None,
) -> str:

    history = history or []

    # Highest priority: explicit prediction request.
    if looks_like_prediction(text):
        return "prediction"

    # Next: explicit correction/update.
    if looks_like_update(text):
        # Only treat as update when it actually contains
        # farm/parameter content.
        if looks_like_parameter_message(text):
            return "parameter_update"

    # Next: explicit general knowledge question.
    # This must come BEFORE farm-data detection.
    if looks_like_knowledge(text):
        return "knowledge"

    # Then explicit personal farm information.
    if looks_like_parameter_message(text):
        return "farm_data"

    # Fall back to context-aware LLM classification.
    return classify_intent(
        text=text,
        history=history,
    ).intent


if __name__ == "__main__":

    tests = [
        "My farm grows Vannamei shrimp.",
        "My pond is 2 acres.",
        "Actually my survival is 85 percent.",
        "What is dissolved oxygen?",
        "Why is oxygen important in shrimp farming?",
        "How do I improve my pond water quality?",
        "Predict my production.",
        "Hello Aqua AI.",
    ]

    for test in tests:
        print(
            f"{test} -> {route_message(test)}"
        )
