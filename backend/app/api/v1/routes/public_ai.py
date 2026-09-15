import json
from typing import Any, Iterator
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
from app.services.parameter_response_service import build_parameter_response
from app.services.conversation_service import (
    get_conversation_messages,
    get_or_create_conversation,
)
from app.services.grounded_rag_service import answer_with_rag
from app.services.fast_router import route_message
from app.services.fast_parameter_extractor import extract_fast
from app.services.live_context_service import (
    is_context_question,
    get_context_answer,
)
from app.services.conversation_context_service import merge_context
from app.services.ai_orchestrator import process_aquaculture_message
from app.services.streaming_rag_service import stream_rag_answer


router = APIRouter(
    prefix="/public/ai",
    tags=["Public AI"],
)


def build_context_prompt(
    context: dict[str, Any],
    message: str,
) -> str:
    return f"""
You are Aqua AI, the aquaculture intelligence assistant for AquaLife.

The user has explicitly provided the following structured farm context:

{json.dumps(context, indent=2)}

Current user message:
{message}

Rules:
- Use the stored context when relevant.
- Never invent missing farm values.
- Never claim access to sensors or records that are not present here.
- Never judge farm performance without supporting evidence.
- Be concise and practical.
""".strip()


def normal_chat_messages(
    context: dict[str, Any],
    history: list[dict[str, str]],
    message: str,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": build_context_prompt(
                context,
                message,
            ),
        },
        *history[-12:],
        {
            "role": "user",
            "content": message,
        },
    ]


def process_structured_context(
    conversation,
    message: str,
    history: list[dict[str, str]],
) -> dict[str, Any]:

    intent = route_message(
        text=message,
        history=history,
    )

    result = {
        "intent": intent,
        "confidence": 1.0,
        "reason": "Fast deterministic routing.",
        "parameters": None,
        "missing_fields": [],
        "ambiguities": [],
        "validation_warnings": [],
    }

    if intent in {
        "farm_data",
        "parameter_update",
    }:

        fast_result = extract_fast(
            message
        )

        if fast_result["success"]:

            result.update(
                {
                    "parameters": fast_result["parameters"],
                    "missing_fields": fast_result["missing_fields"],
                    "ambiguities": fast_result["ambiguities"],
                    "validation_warnings": fast_result[
                        "validation_warnings"
                    ],
                }
            )

        else:

            from app.services.parameter_extraction_engine import (
                extract_normalize_validate,
            )

            extracted = extract_normalize_validate(
                message
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

        conversation.context_data = merge_context(
            conversation.context_data,
            result["parameters"],
        )

    return result


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

        sources: list[PublicAiSource] = []

        # 1. Simple structured-memory lookup.
        if is_context_question(data.message):
            answer = get_context_answer(
                conversation.context_data or {},
                data.message,
            )

        else:
            # 2. Intent + extraction + normalization + validation.
            result = process_structured_context(
                conversation,
                data.message,
                history,
            )

            # 3. Knowledge/RAG.
            if result["intent"] == "knowledge":
                rag_result = answer_with_rag(
                    data.message,
                    limit=3,
                )

                answer = rag_result["answer"]

                sources = [
                    PublicAiSource(**source)
                    for source in rag_result["sources"]
                ]

            # 4. Farm data / parameter updates.
            elif result["intent"] in {
                "farm_data",
                "parameter_update",
            }:
                answer = build_parameter_response(
                    result["intent"],
                    result["parameters"] or {},
                )

            # 5. Other messages.
            else:
                answer = provider.chat(
                    normal_chat_messages(
                        conversation.context_data or {},
                        history,
                        data.message,
                    ),
                    temperature=0.1,
                    think=False,
                )

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

        # Instant context answer: stream it as one small event.
        if is_context_question(data.message):

            answer = get_context_answer(
                conversation.context_data or {},
                data.message,
            )

            iterator = iter([answer])
            sources = []

        else:

            result = process_structured_context(
                conversation,
                data.message,
                history,
            )

            if result["intent"] == "knowledge":

                iterator, sources = stream_rag_answer(
                    data.message,
                    limit=3,
                )

            elif result["intent"] in {
                "farm_data",
                "parameter_update",
            }:

                iterator = iter([
                    build_parameter_response(
                        result["intent"],
                        result["parameters"] or {},
                    )
                ])

                sources = []

            else:

                iterator = provider.chat_stream(
                    normal_chat_messages(
                        conversation.context_data or {},
                        history,
                        data.message,
                    ),
                    temperature=0.1,
                    think=False,
                )

                sources = []

        def event_stream() -> Iterator[str]:

            yield (
                "data: "
                + json.dumps(
                    {
                        "type": "meta",
                        "conversation_id": str(
                            conversation.id
                        ),
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

            full_answer: list[str] = []

            try:
                for token in iterator:

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
                        {"type": "done"}
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
