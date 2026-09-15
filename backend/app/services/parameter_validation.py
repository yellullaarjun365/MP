from pydantic import BaseModel, Field


SPECIES_ALIASES = {
    "vannamei": "Litopenaeus vannamei",
    "vannamei shrimp": "Litopenaeus vannamei",
    "white shrimp": "Litopenaeus vannamei",
    "litopenaeus vannamei": "Litopenaeus vannamei",
    "tiger shrimp": "Penaeus monodon",
    "black tiger shrimp": "Penaeus monodon",
    "penaeus monodon": "Penaeus monodon",
    "tilapia": "Oreochromis niloticus",
    "nile tilapia": "Oreochromis niloticus",
    "oreochromis niloticus": "Oreochromis niloticus",
    "giant river prawn": "Macrobrachium rosenbergii",
    "freshwater prawn": "Macrobrachium rosenbergii",
    "macrobrachium rosenbergii": "Macrobrachium rosenbergii",
}


AREA_UNITS = {
    "m2": "m2",
    "m²": "m2",
    "square meter": "m2",
    "square meters": "m2",
    "sq meter": "m2",
    "sq meters": "m2",
    "sqm": "m2",
    "acre": "acre",
    "acres": "acre",
    "ha": "ha",
    "hectare": "ha",
    "hectares": "ha",
}


class NormalizedParameters(BaseModel):
    species: str | None = None

    pond_area: float | None = Field(
        default=None,
        ge=0,
    )

    pond_area_unit: str | None = None

    pond_volume_m3: float | None = Field(
        default=None,
        ge=0,
    )

    stocking_count: int | None = Field(
        default=None,
        ge=0,
    )

    average_weight_g: float | None = Field(
        default=None,
        ge=0,
    )

    survival_rate_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    temperature_c: float | None = None

    ph: float | None = Field(
        default=None,
        ge=0,
        le=14,
    )

    dissolved_oxygen_mg_l: float | None = Field(
        default=None,
        ge=0,
    )

    salinity_ppt: float | None = Field(
        default=None,
        ge=0,
    )

    feed_kg_per_day: float | None = Field(
        default=None,
        ge=0,
    )


def normalize_species(
    species: str | None,
) -> str | None:

    if species is None:
        return None

    key = species.strip().lower()

    return SPECIES_ALIASES.get(
        key,
        species.strip(),
    )


def normalize_area_unit(
    unit: str | None,
) -> str | None:

    if unit is None:
        return None

    key = unit.strip().lower()

    return AREA_UNITS.get(
        key,
        key,
    )


def normalize_parameters(
    parameters,
) -> NormalizedParameters:

    data = parameters.model_dump()

    data["species"] = normalize_species(
        data.get("species")
    )

    data["pond_area_unit"] = normalize_area_unit(
        data.get("pond_area_unit")
    )

    return NormalizedParameters.model_validate(
        data
    )


def validate_business_rules(
    parameters: NormalizedParameters,
) -> list[str]:

    warnings = []

    if (
        parameters.pond_area is not None
        and parameters.pond_area_unit is None
    ):
        warnings.append(
            "Pond area was provided without a unit."
        )

    if (
        parameters.stocking_count is not None
        and parameters.pond_area is not None
        and parameters.pond_area_unit == "m2"
        and parameters.pond_area > 0
    ):
        density = (
            parameters.stocking_count
            / parameters.pond_area
        )

        if density > 100:
            warnings.append(
                "Stocking density is unusually high; verify the values."
            )

    if (
        parameters.average_weight_g is not None
        and parameters.average_weight_g > 500
    ):
        warnings.append(
            "Average weight is unusually high; verify the value."
        )

    if (
        parameters.temperature_c is not None
        and (
            parameters.temperature_c < 0
            or parameters.temperature_c > 50
        )
    ):
        warnings.append(
            "Temperature should be verified."
        )

    return warnings


print("Parameter validation module: OK")
