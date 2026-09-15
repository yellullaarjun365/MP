from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.services.ai_orchestrator import (
    process_aquaculture_message,
)


CONTEXT_FIELDS = [
    "species",
    "pond_area",
    "pond_area_unit",
    "pond_volume_m3",
    "stocking_count",
    "average_weight_g",
    "survival_rate_percent",
    "temperature_c",
    "ph",
    "dissolved_oxygen_mg_l",
    "salinity_ppt",
    "feed_kg_per_day",
]


def merge_context(
    current: dict[str, Any] | None,
    incoming: dict[str, Any] | None,
) -> dict[str, Any]:

    current = dict(current or {})
    incoming = incoming or {}

    for field in CONTEXT_FIELDS:
        value = incoming.get(field)

        if value is not None:
            current[field] = value

    return current


def get_conversation(
    db: Session,
    conversation_id,
) -> Conversation | None:

    return db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id
        )
    )


def process_and_persist_context(
    db: Session,
    conversation_id,
    text: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:

    conversation = get_conversation(
        db,
        conversation_id,
    )

    if conversation is None:
        raise ValueError(
            "Conversation not found."
        )

    result = process_aquaculture_message(
        text=text,
        history=history,
    )

    if result["parameters"] is not None:

        conversation.context_data = merge_context(
            conversation.context_data,
            result["parameters"],
        )

        db.commit()
        db.refresh(conversation)

    result["context_data"] = (
        conversation.context_data or {}
    )

    return result


__all__ = [
    "merge_context",
    "process_and_persist_context",
]
