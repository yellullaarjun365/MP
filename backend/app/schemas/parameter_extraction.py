from pydantic import BaseModel


class ParameterExtractionRequest(BaseModel):
    text: str


class ParameterExtractionResponse(BaseModel):
    original_text: str
    parameters: dict
    missing_fields: list[str]
    ambiguities: list[str]
    validation_warnings: list[str]
