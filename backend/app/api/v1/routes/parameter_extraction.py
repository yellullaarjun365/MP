from fastapi import APIRouter, HTTPException

from app.ai.ollama import OllamaError
from app.schemas.parameter_extraction import (
    ParameterExtractionRequest,
    ParameterExtractionResponse,
)
from app.services.parameter_extraction_engine import (
    extract_normalize_validate,
)


router = APIRouter(
    prefix="/parameter-extraction",
    tags=["Parameter Extraction"],
)


@router.post(
    "",
    response_model=ParameterExtractionResponse,
)
def extract_parameters(
    data: ParameterExtractionRequest,
):

    try:
        return extract_normalize_validate(
            data.text
        )

    except OllamaError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Parameter extraction error: {exc}",
        ) from exc
