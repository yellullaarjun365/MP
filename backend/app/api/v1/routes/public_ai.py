import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.ollama import OllamaError, provider
from app.ai.service import ai_status
from app.api.deps import get_optional_user_id
from app.db.session import get_db
from app.models.message import Message
from app.schemas.public_ai import (
    PublicAiChatRequest,
    PublicAiChatResponse,
    PublicAiSource,
    PublicAiStatusResponse,
)
from app.services.conversation_service import (
    get_conversation_messages,
    get_or_create_conversation,
)
from app.services.grounded_rag_service import answer_with_rag
from app.services.streaming_rag_service import stream_rag_answer


router = APIRouter(
    prefix="/public/ai",
    tags=["Public AI"],
)


MEMORY_TERMS = [
    "did i say",
    "did i tell you",
    "what did i tell you",
    "what did i say",
    "as i mentioned",
    "i mentioned",
    "i told you",
    "you remember",
    "do you remember",
    "my farm",
    "my pond",
    "my species",
    "previous message",
    "earlier",
    "before",
]


PERSONAL_CONTEXT_STARTS = [
    "my ",
    "i have ",
    "i grow ",
    "i farm ",
    "i use ",
    "our farm ",
    "our pond ",
    "we grow ",
    "we farm ",
]


KNOWLEDGE_TERMS = [
    "what is",
    "why",
    "how does",
    "how do",
    "explain",
    "aquaculture",
    "shrimp",
    "fish",
    "tilapia",
    "prawn",
    "water quality",
    "dissolved oxygen",
    "oxygen",
    "ph",
    "salinity",
    "temperature",
    "feeding",
    "stocking",
    "biomass",
    "disease",
]


def is_memory_question(message: str) -> bool:
    text = message.lower().strip()
    return any(term in text for term in MEMORY_TERMS)


def is_personal_context(message: str) -> bool:
    text = message.lower().strip()
    return any(text.startswith(prefix) for prefix in PERSONAL_CONTEXT_STARTS)


def is_knowledge_question(message: str) -> bool:
    text = message.lower().strip()
    return any(term in text for term in KNOWLEDGE_TERMS)


def answer_from_conversation(
    history: list[dict[str, str]],
    message: str,
) -> str:

    messages = [
        {
            "role": "system",
            "content": (
                "You are Aqua AI, the aquaculture intelligence "
                "assistant for AquaLife. Use conversation history "
                "to remember facts explicitly provided by the user. "
                "Do not invent farm or personal information. "
                "Be concise and practical."
            ),
        },
        *history,
        {
            "role": "user",
            "content": message,
        },
    ]

    return provider.chat(
        messages,
        temperature=0.1,
        think=False,
    )


@router.get(
    "/status",
    response_model=PublicAiStatusResponse,
)
def public_ai_status():
    return ai_status()


@router.post(
    "/chat",
    response_model=PublicAiChatResponse,
)
def public_ai_chat(
    data: PublicAiChatRequest,
    db: Session = Depends(get_db),
    user_id: UUID | None = Depends(get_optional_user_id),
):
    try:
        conversation = get_or_create_conversation(
            db=db,
            user_id=user_id,
            conversation_id=data.conversation_id,
            title=data.message[:80],
        )

        history = get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )

        if (
            is_memory_question(data.message)
            or is_personal_context(data.message)
        ):
            answer = answer_from_conversation(
                history=history,
                message=data.message,
            )
            sources = []

        elif is_knowledge_question(data.message):
            result = answer_with_rag(
                question=data.message,
                limit=3,
            )
            answer = result["answer"]
            sources = [
                PublicAiSource(**source)
                for source in result["sources"]
            ]

        else:
            answer = answer_from_conversation(
                history=history,
                message=data.message,
            )
            sources = []

        db.add(
            Message(
                conversation_id=conversation.id,
                role="user",
                content=data.message,
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

        return PublicAiChatResponse(
            answer=answer,
            model=provider.model,
            mode="authenticated" if user_id else "guest",
            conversation_id=conversation.id,
            sources=sources,
        )

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except OllamaError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aqua AI error: {exc}",
        ) from exc


@router.post("/chat/stream")
def public_ai_chat_stream(
    data: PublicAiChatRequest,
    db: Session = Depends(get_db),
    user_id: UUID | None = Depends(get_optional_user_id),
):
    try:
        conversation = get_or_create_conversation(
            db=db,
            user_id=user_id,
            conversation_id=data.conversation_id,
            title=data.message[:80],
        )

        history = get_conversation_messages(
            db=db,
            conversation_id=conversation.id,
        )

        memory_question = is_memory_question(data.message)
        personal_context = is_personal_context(data.message)
        knowledge_question = is_knowledge_question(data.message)

        if knowledge_question and not memory_question and not personal_context:
            token_iterator, sources = stream_rag_answer(
                question=data.message,
                limit=3,
            )
        else:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are Aqua AI, the aquaculture intelligence "
                        "assistant for AquaLife. Use conversation history "
                        "to remember facts explicitly provided by the user. "
                        "Do not invent farm or personal information. "
                        "Be concise and practical."
                    ),
                },
                *history,
                {
                    "role": "user",
                    "content": data.message,
                },
            ]

            token_iterator = provider.chat_stream(
                messages,
                temperature=0.1,
                think=False,
            )

            sources = []

        def event_stream():
            full_answer = []

            yield (
                "data: "
                + json.dumps(
                    {
                        "type": "meta",
                        "conversation_id": str(conversation.id),
                        "model": provider.model,
                        "mode": (
                            "authenticated"
                            if user_id
                            else "guest"
                        ),
                    }
                )
                + "\n\n"
            )

            try:
                for token in token_iterator:
                    full_answer.append(token)

                    yield (
                        "data: "
                        + json.dumps(
                            {
                                "type": "token",
                                "content": token,
                            },
                            ensure_ascii=False,
                        )
                        + "\n\n"
                    )

                answer = "".join(full_answer).strip()

                db.add(
                    Message(
                        conversation_id=conversation.id,
                        role="user",
                        content=data.message,
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

                if sources:
                    yield (
                        "data: "
                        + json.dumps(
                            {
                                "type": "sources",
                                "sources": sources,
                            },
                            ensure_ascii=False,
                        )
                        + "\n\n"
                    )

                yield (
                    "data: "
                    + json.dumps(
                        {
                            "type": "done",
                        }
                    )
                    + "\n\n"
                )

            except Exception as exc:
                db.rollback()

                yield (
                    "data: "
                    + json.dumps(
                        {
                            "type": "error",
                            "detail": str(exc),
                        }
                    )
                    + "\n\n"
                )

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aqua AI stream error: {exc}",
        ) from exc
