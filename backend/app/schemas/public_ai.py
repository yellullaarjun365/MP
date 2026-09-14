from pydantic import BaseModel, Field


class PublicAiChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )


class PublicAiChatResponse(BaseModel):
    answer: str
    model: str
    mode: str


class PublicAiStatusResponse(BaseModel):
    available: bool
    model: str
    model_installed: bool
    base_url: str
    mode: str
    authentication_required: bool
