import re
from typing import Any

from app.services.parameter_validation import (
    normalize_parameters,
    validate_business_rules,
)
from app.schemas.aquaculture_parameters import (
    AquacultureParameters,
)


SPECIES_PATTERNS = [
    (r"\bvannamei\b", "Litopenaeus vannamei"),
    (r"\bvannamei shrimp\b", "Litopenaeus vannamei"),
    (r"\bwhite shrimp\b", "Litopenaeus vannamei"),
    (r"\bpenaeus monodon\b", "Penaeus monodon"),
    (r"\btiger shrimp\b", "Penaeus monodon"),
    (r"\bblack tiger shrimp\b", "Penaeus monodon"),
    (r"\bnile tilapia\b", "Oreochromis niloticus"),
    (r"\btilapia\b", "Oreochromis niloticus"),
    (r"\bmacrobrachium rosenbergii\b", "Macrobrachium rosenbergii"),
    (r"\bgiant river prawn\b", "Macrobrachium rosenbergii"),
    (r"\bfreshwater prawn\b", "Macrobrachium rosenbergii"),
]


def extract_species(text: str) -> str | None:
    value = text.lower()

    for pattern, species in SPECIES_PATTERNS:
        if re.search(pattern, value):
            return species

    return None


def extract_number(
    patterns: list[str],
    text: str,
) -> float | None:

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return float(
                match.group(1).replace(",", "")
            )

    return None


def deterministic_extract(
    text: str,
) -> dict[str, Any]:

    result: dict[str, Any] = {
        "species": extract_species(text),
        "pond_area": None,
        "pond_area_unit": None,
        "pond_volume_m3": None,
        "stocking_count": None,
        "average_weight_g": None,
        "survival_rate_percent": None,
        "temperature_c": None,
        "ph": None,
        "dissolved_oxygen_mg_l": None,
        "salinity_ppt": None,
        "feed_kg_per_day": None,
    }

    # Pond area
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(acre|acres|ha|hectare|hectares|m2|m²|sqm|square\s*meters?|sq\s*meters?)",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        result["pond_area"] = float(match.group(1))
        result["pond_area_unit"] = (
            match.group(2)
        )

    # Pond volume
    result["pond_volume_m3"] = extract_number(
        [
            r"(?:pond\s+)?volume\s*(?:is|=|of)?\s*([\d,.]+)\s*(?:m3|m³|cubic\s*meters?)",
        ],
        text,
    )

    # Stocking count
    result["stocking_count"] = extract_number(
        [
            r"(?:stocked|stocking(?:\s+count|\s+number)?|stocking\s+of)\s*[:=]?\s*([\d,]+)",
            r"([\d,]+)\s*(?:vannamei|shrimp|prawns?)",
        ],
        text,
    )

    if result["stocking_count"] is not None:
        result["stocking_count"] = int(
            result["stocking_count"]
        )

    # Average weight
    result["average_weight_g"] = extract_number(
        [
            r"(?:average\s+weight|avg(?:erage)?\s+weight)\s*(?:is|=|of)?\s*([\d.]+)\s*g",
            r"(?:shrimp|prawn)s?\s*(?:are|average)\s*(?:around|about)?\s*([\d.]+)\s*g",
        ],
        text,
    )

    # Survival
    result["survival_rate_percent"] = extract_number(
        [
            r"(?:survival|survival\s+rate)\s*(?:is|=|of)?\s*([\d.]+)\s*%",
            r"survival\s*(?:is|at)\s*([\d.]+)\s*percent",
        ],
        text,
    )

    # Temperature
    result["temperature_c"] = extract_number(
        [
            r"(?:temperature|temp)\s*(?:is|=|of)?\s*([\d.]+)\s*(?:°?\s*c|celsius)",
        ],
        text,
    )

    # pH
    result["ph"] = extract_number(
        [
            r"\bpH\s*(?:is|=|of)?\s*([\d.]+)",
        ],
        text,
    )

    # Dissolved oxygen
    result["dissolved_oxygen_mg_l"] = extract_number(
        [
            r"(?:dissolved\s+oxygen|DO)\s*(?:is|=|of)?\s*([\d.]+)\s*(?:mg/?l|mg\s*per\s*liter)",
        ],
        text,
    )

    # Salinity
    result["salinity_ppt"] = extract_number(
        [
            r"(?:salinity)\s*(?:is|=|of)?\s*([\d.]+)\s*(?:ppt|psu)",
        ],
        text,
    )

    # Feed
    result["feed_kg_per_day"] = extract_number(
        [
            r"(?:feed|feeding)\s*(?:is|=|of)?\s*([\d.]+)\s*(?:kg|kilograms?)\s*(?:per\s*day|/day)",
        ],
        text,
    )

    return result


def has_deterministic_data(
    data: dict[str, Any],
) -> bool:

    return any(
        value is not None
        for value in data.values()
    )


def extract_fast(
    text: str,
) -> dict[str, Any]:

    raw = deterministic_extract(text)

    if not has_deterministic_data(raw):
        return {
            "success": False,
            "parameters": None,
        }

    parameters = AquacultureParameters.model_validate(
        raw
    )

    normalized = normalize_parameters(
        parameters
    )

    warnings = validate_business_rules(
        normalized
    )

    missing = [
        field
        for field, value in normalized.model_dump().items()
        if value is None
    ]

    return {
        "success": True,
        "parameters": normalized.model_dump(),
        "missing_fields": missing,
        "ambiguities": [],
        "validation_warnings": warnings,
    }


__all__ = [
    "deterministic_extract",
    "extract_fast",
    "has_deterministic_data",
]
