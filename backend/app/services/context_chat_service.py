from typing import Any

from app.ai.ollama import provider
from app.models.conversation import Conversation
from app.services.conversation_context_service import (
    merge_context,
)
from app.services.ai_orchestrator import (
    process_aquaculture_message,
)


def context_summary(
    context: dict[str, Any],
) -> str:

    if not context:
        return "No structured farm information has been provided yet."

    labels = {
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

    lines = []

    for key, value in context.items():

        label = labels.get(
            key,
            key,
        )

        lines.append(
            f"- {label}: {value}"
        )

    return "\n".join(lines)


def answer_with_context(
    conversation: Conversation,
    message: str,
    history: list[dict[str, str]],
) -> tuple[str, dict]:

    result = process_aquaculture_message(
        text=message,
        history=history,
    )

    if result["parameters"] is not None:

        conversation.context_data = merge_context(
            conversation.context_data,
            result["parameters"],
        )

    context = conversation.context_data or {}

    prompt = f"""
You are Aqua AI, the aquaculture intelligence assistant for AquaLife.

The user has a structured conversation context.

CURRENT FARM CONTEXT:
{context_summary(context)}

USER MESSAGE:
{message}

Rules:

- Use the structured context when answering questions about the user's farm.
- Never invent values that are not present in the context.
- If the user asks about something stored in context, answer directly.
- If information is missing, say which information is missing.
- Keep the response concise and practical.
""".strip()

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
    "answer_with_context",
]
