from pydantic import BaseModel


class VoiceTranscriptionResponse(BaseModel):
    text: str
    raw_text: str
    language: str | None
    language_probability: float | None
    model: str
    normalized: bool
