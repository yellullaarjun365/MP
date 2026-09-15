from typing import Any


LABELS = {
    "species": "Species",
    "pond_area": "Pond area",
    "pond_volume_m3": "Pond volume",
    "stocking_count": "Stocking count",
    "average_weight_g": "Average weight",
    "survival_rate_percent": "Survival rate",
    "temperature_c": "Temperature",
    "ph": "pH",
    "dissolved_oxygen_mg_l": "Dissolved oxygen",
    "salinity_ppt": "Salinity",
    "feed_kg_per_day": "Feed",
}


def format_value(
    field: str,
    value: Any,
) -> str:

    if field == "pond_area":
        return f"{value:g}"

    if field == "stocking_count":
        return f"{int(value):,}"

    if field == "average_weight_g":
        return f"{value:g} g"

    if field == "survival_rate_percent":
        return f"{value:g}%"

    if field == "temperature_c":
        return f"{value:g} °C"

    if field == "ph":
        return f"{value:g}"

    if field == "dissolved_oxygen_mg_l":
        return f"{value:g} mg/L"

    if field == "salinity_ppt":
        return f"{value:g} ppt"

    if field == "feed_kg_per_day":
        return f"{value:g} kg/day"

    if field == "pond_volume_m3":
        return f"{value:g} m³"

    if field == "pond_area_unit":
        return str(value)

    return str(value)


def build_parameter_response(
    intent: str,
    parameters: dict[str, Any],
) -> str:

    present = [
        (field, value)
        for field, value in parameters.items()
        if value is not None
        and field in LABELS
        and field != "pond_area_unit"
    ]

    if not present:
        return (
            "I did not detect any new farm parameters "
            "in that message."
        )

    if intent == "parameter_update":
        prefix = "I updated the following farm information:"
    else:
        prefix = "I recorded the following farm information:"

    lines = [prefix]

    for field, value in present:
        label = LABELS[field]

        if field == "pond_area":
            unit = parameters.get(
                "pond_area_unit"
            )

            if unit:
                value_text = (
                    f"{value:g} {unit}"
                )
            else:
                value_text = f"{value:g}"

        else:
            value_text = format_value(
                field,
                value,
            )

        lines.append(
            f"- {label}: {value_text}"
        )

    return "\n".join(lines)


__all__ = [
    "build_parameter_response",
]
