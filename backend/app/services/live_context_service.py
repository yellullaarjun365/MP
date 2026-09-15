from typing import Any

from app.ai.ollama import provider
from app.models.conversation import Conversation
from app.services.conversation_context_service import (
    merge_context,
)
from app.services.ai_orchestrator import (
    process_aquaculture_message,
)


CONTEXT_QUESTION_PATTERNS = [
    "what species am i farming",
    "what species am i growing",
    "what shrimp species am i farming",
    "what shrimp do i farm",
    "how many shrimp did i stock",
    "how many shrimp have i stocked",
    "what is my stocking count",
    "what is my pond area",
    "how big is my pond",
    "what is my pond size",
    "what is my survival rate",
    "what is my temperature",
    "what is my ph",
    "what is my dissolved oxygen",
    "what is my salinity",
]


CONTEXT_LABELS = {
    "species": "Species",
    "pond_area": "Pond area",
    "pond_area_unit": "Area unit",
    "pond_volume_m3": "Pond volume (m³)",
    "stocking_count": "Stocking count",
    "average_weight_g": "Average weight (g)",
    "survival_rate_percent": "Survival rate (%)",
    "temperature_c": "Temperature (°C)",
    "ph": "pH",
    "dissolved_oxygen_mg_l": "Dissolved oxygen (mg/L)",
    "salinity_ppt": "Salinity (ppt)",
    "feed_kg_per_day": "Feed (kg/day)",
}


def is_context_question(
    text: str,
) -> bool:

    normalized = " ".join(
        text.lower().strip().split()
    )

    return any(
        pattern in normalized
        for pattern in CONTEXT_QUESTION_PATTERNS
    )


def get_context_answer(
    context: dict[str, Any],
    question: str,
) -> str:

    normalized = question.lower()

    if (
        "species" in normalized
        and context.get("species")
    ):
        return (
            f"You are farming {context['species']}."
        )

    if (
        (
            "how many shrimp" in normalized
            or "stocking count" in normalized
        )
        and context.get("stocking_count") is not None
    ):
        return (
            f"Your stocking count is "
            f"{context['stocking_count']:,} shrimp."
        )

    if (
        "pond area" in normalized
        or "pond size" in normalized
        or "how big is my pond" in normalized
    ):

        if context.get("pond_area") is not None:
            return (
                f"Your pond area is "
                f"{context['pond_area']} "
                f"{context.get('pond_area_unit', '')}."
            ).strip()

    field_map = {
        "survival": "survival_rate_percent",
        "temperature": "temperature_c",
        " pH": "ph",
        "dissolved oxygen": "dissolved_oxygen_mg_l",
        "salinity": "salinity_ppt",
    }

    for keyword, field in field_map.items():

        if (
            keyword.strip() in normalized
            and context.get(field) is not None
        ):
            return (
                f"Your {CONTEXT_LABELS[field].lower()} "
                f"is {context[field]}."
            )

    available = [
        f"{CONTEXT_LABELS[key]}: {value}"
        for key, value in context.items()
        if value is not None
        and key in CONTEXT_LABELS
    ]

    if available:
        return (
            "Here is the farm information I currently have:\n"
            + "\n".join(
                f"- {item}"
                for item in available
            )
        )

    return (
        "I don't have that farm information recorded "
        "in the current conversation."
    )


def build_context_prompt(
    context: dict[str, Any],
    message: str,
) -> str:

    lines = []

    for key, value in context.items():

        if key in CONTEXT_LABELS:
            lines.append(
                f"- {CONTEXT_LABELS[key]}: {value}"
            )

    context_text = (
        "\n".join(lines)
        if lines
        else "No structured farm information is recorded."
    )

    return f"""
You are Aqua AI for AquaLife.

The following information was explicitly provided by the user
and stored as structured conversation context:

{context_text}

Current user message:
{message}

Rules:
- Use stored context when relevant.
- Never invent missing farm values.
- Never praise, criticize, or judge farm performance unless the
  supplied evidence explicitly supports that conclusion.
- Do not create new numerical values unless they are simple,
  transparent arithmetic directly requested or obviously required.
- State when information is missing.
- Be concise and practical.
""".strip()


def process_live_message(
    conversation: Conversation,
    message: str,
    history: list[dict[str, str]],
) -> tuple[str, dict[str, Any]]:

    if is_context_question(
        message
    ):
        answer = get_context_answer(
            conversation.context_data or {},
            message,
        )

        return answer, {
            "intent": "context_question",
            "parameters": None,
            "missing_fields": [],
            "ambiguities": [],
            "validation_warnings": [],
        }

    result = process_aquaculture_message(
        text=message,
        history=history,
    )

    if result["parameters"] is not None:

        conversation.context_data = merge_context(
            conversation.context_data,
            result["parameters"],
        )

    prompt = build_context_prompt(
        conversation.context_data or {},
        message,
    )

    answer = provider.chat(
        [
            {
                "role": "system",
                "content": prompt,
            },
            *history,
            {
                "role": "user",
                "content": message,
            },
        ],
        temperature=0.1,
        think=False,
    )

    return answer, result


__all__ = [
    "is_context_question",
    "get_context_answer",
    "process_live_message",
]
