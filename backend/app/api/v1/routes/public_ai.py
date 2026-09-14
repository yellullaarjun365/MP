from fastapi import APIRouter, HTTPException, status

from app.ai.service import (
    OllamaError,
    ai_status,
    answer_guest_question,
)
from app.ai.ollama import provider
from app.schemas.public_ai import (
    PublicAiChatRequest,
    PublicAiChatResponse,
    PublicAiStatusResponse,
)


router = APIRouter(
    prefix="/public/ai",
    tags=["Public AI"],
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
):
    try:
        answer = answer_guest_question(
            data.message
        )

        return PublicAiChatResponse(
            answer=answer,
            model=provider.model,
            mode="guest",
        )

    except OllamaError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aqua AI error: {exc}",
        ) from exc
