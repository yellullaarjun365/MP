from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.ollama import provider
from app.ai.service import AQUA_SYSTEM_PROMPT
from app.models.conversation import Conversation
from app.models.message import Message


def get_or_create_conversation(
    db: Session,
    user_id: UUID | None,
    conversation_id: UUID | None = None,
    title: str | None = None,
) -> Conversation:

    if conversation_id is not None:
        conversation = db.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id
            )
        )

        if conversation is not None:
            if user_id is None or conversation.user_id == user_id:
                return conversation

            raise ValueError(
                "Conversation does not belong to this user."
            )

    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)
    db.flush()

    return conversation


def get_conversation_messages(
    db: Session,
    conversation_id: UUID,
) -> list[dict[str, str]]:

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.id)
    )

    messages = db.scalars(statement).all()

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


def chat_with_memory(
    db: Session,
    user_id: UUID | None,
    message: str,
    conversation_id: UUID | None = None,
) -> tuple[Conversation, str]:

    conversation = get_or_create_conversation(
        db=db,
        user_id=user_id,
        conversation_id=conversation_id,
        title=message[:80],
    )

    history = get_conversation_messages(
        db=db,
        conversation_id=conversation.id,
    )

    messages = [
        {
            "role": "system",
            "content": AQUA_SYSTEM_PROMPT.replace(
                "You are currently operating in GUEST MODE.",
                "You are operating in conversational memory mode.",
            ).strip(),
        },
        *history,
        {
            "role": "user",
            "content": message.strip(),
        },
    ]

    answer = provider.chat(messages)

    db.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content=message.strip(),
        )
    )

    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )
    )

    db.commit()
    db.refresh(conversation)

    return conversation, answer
