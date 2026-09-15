from uuid import UUID

from pydantic import BaseModel, Field


class PublicAiSource(BaseModel):
    source_file: str
    page: int
    chunk_index: int
    similarity: float


class PublicAiChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    conversation_id: UUID | None = None


class PublicAiChatResponse(BaseModel):
    answer: str
    model: str
    mode: str
    conversation_id: UUID
    sources: list[PublicAiSource] = []


class PublicAiStatusResponse(BaseModel):
    available: bool
    model: str
    model_installed: bool
    base_url: str
    mode: str
    authentication_required: bool
