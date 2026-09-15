import json
from typing import Any

from app.ai.ollama import provider
from app.schemas.aquaculture_parameters import (
    ExtractionResult,
)
from app.services.parameter_extraction import (
    compute_missing_fields,
)
from app.services.parameter_validation import (
    NormalizedParameters,
    normalize_parameters,
    validate_business_rules,
)


EXTRACTION_PROMPT = """
You are AquaLife's structured aquaculture parameter extraction engine.

Extract ONLY information explicitly stated by the user.

Return ONLY valid JSON with this exact shape:

{
  "parameters": {
    "species": null,
    "pond_area": null,
    "pond_area_unit": null,
    "pond_volume_m3": null,
    "stocking_count": null,
    "average_weight_g": null,
    "survival_rate_percent": null,
    "temperature_c": null,
    "ph": null,
    "dissolved_oxygen_mg_l": null,
    "salinity_ppt": null,
    "feed_kg_per_day": null
  },
  "missing_fields": [],
  "ambiguities": []
}

Rules:
- Extract only facts explicitly stated by the user.
- Never guess missing values.
- Never invent measurements.
- Never silently convert units.
- Use null for values that were not provided.
- Put unclear or conflicting information in ambiguities.
- Return JSON only.
""".strip()


def extract_from_text(
    text: str,
) -> ExtractionResult:

    response = provider.chat(
        [
            {
                "role": "system",
                "content": EXTRACTION_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.0,
        think=False,
    )

    raw = response.strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip("` \n")

    return ExtractionResult.model_validate(
        json.loads(raw)
    )


def extract_normalize_validate(
    text: str,
) -> dict[str, Any]:

    extracted = extract_from_text(text)

    normalized: NormalizedParameters = (
        normalize_parameters(
            extracted.parameters
        )
    )

    missing = compute_missing_fields(
        normalized
    )

    warnings = validate_business_rules(
        normalized
    )

    return {
        "original_text": text,
        "parameters": normalized.model_dump(),
        "missing_fields": missing,
        "ambiguities": extracted.ambiguities,
        "validation_warnings": warnings,
    }


__all__ = [
    "extract_from_text",
    "extract_normalize_validate",
]
