import re


DOMAIN_CORRECTIONS = [
    (
        r"\bone[- ]armed\s+my\s+stream\b",
        "Vannamei shrimp",
    ),
    (
        r"\bone[- ]armed\s+shrimp\b",
        "Vannamei shrimp",
    ),
    (
        r"\bvanamei\b",
        "Vannamei",
    ),
    (
        r"\bvanami\b",
        "Vannamei",
    ),
    (
        r"\bvaname\b",
        "Vannamei",
    ),
    (
        r"\bvannamee\b",
        "Vannamei",
    ),
    (
        r"\bwhite\s+shrimp\b",
        "Vannamei shrimp",
    ),
    (
        r"\bstalked\b",
        "stocked",
    ),
    (
        r"\bstream\b",
        "shrimp",
    ),
]


def normalize_voice_transcript(
    text: str,
    language: str | None = None,
) -> str:

    normalized = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    # Only apply the English aquaculture correction
    # dictionary to English transcripts.
    #
    # Telugu must pass through unchanged.
    if (
        language is not None
        and not language.lower().startswith("en")
    ):
        return normalized

    for pattern, replacement in DOMAIN_CORRECTIONS:
        normalized = re.sub(
            pattern,
            replacement,
            normalized,
            flags=re.IGNORECASE,
        )

    return re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()


__all__ = [
    "normalize_voice_transcript",
]
