from fastapi import APIRouter
from pydantic import BaseModel, Field


class PublicAiChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class PublicAiChatResponse(BaseModel):
    answer: str


router = APIRouter(
    prefix="/public/ai",
    tags=["Public AI"],
)


@router.get("/status")
def public_ai_status():
    return {
        "available": True,
        "mode": "guest",
        "authentication_required": False,
    }


@router.post(
    "/chat",
    response_model=PublicAiChatResponse,
)
def public_ai_chat(data: PublicAiChatRequest):
    return PublicAiChatResponse(
        answer=(
            "Aqua AI guest mode is connected. "
            "This public assistant currently provides the "
            "guest-mode response layer."
        )
    )
