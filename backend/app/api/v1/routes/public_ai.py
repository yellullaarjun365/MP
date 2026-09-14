from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.ollama import OllamaError, provider
from app.ai.service import ai_status
from app.api.deps import get_optional_user_id
from app.db.session import get_db
from app.schemas.public_ai import (
    PublicAiChatRequest,
    PublicAiChatResponse,
    PublicAiStatusResponse,
)
from app.services.conversation_service import chat_with_memory


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
    db: Session = Depends(get_db),
    user_id: UUID | None = Depends(get_optional_user_id),
):
    try:
        conversation, answer = chat_with_memory(
            db=db,
            user_id=user_id,
            message=data.message,
            conversation_id=data.conversation_id,
        )

        return PublicAiChatResponse(
            answer=answer,
            model=provider.model,
            mode="authenticated" if user_id else "guest",
            conversation_id=conversation.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

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
