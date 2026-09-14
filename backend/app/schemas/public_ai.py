from pydantic import BaseModel, Field


class PublicAiChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class PublicAiChatResponse(BaseModel):
    answer: str
