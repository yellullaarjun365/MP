from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "manifests"
    / "production-evidence-v1.json"
)


def load_manifest(
    path: str | Path = DEFAULT_MANIFEST,
) -> dict:
    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        return json.load(file)


def validate_manifest(
    manifest: dict,
) -> list[str]:
    errors: list[str] = []

    variables = manifest.get(
        "variables",
        {},
    )

    sources = manifest.get(
        "sources",
        [],
    )

    relationships = manifest.get(
        "relationships",
        [],
    )

    constraints = manifest.get(
        "constraints",
        [],
    )

    policy = manifest.get(
        "generator_policy",
    )

    target_policy = manifest.get(
        "target_policy",
    )

    if not sources:
        errors.append(
            "manifest.sources is empty"
        )

    if not relationships:
        errors.append(
            "manifest.relationships is empty"
        )

    if not constraints:
        errors.append(
            "manifest.constraints is empty"
        )

    if not policy:
        errors.append(
            "manifest.generator_policy is missing"
        )
        return errors

    enabled = policy.get(
        "enabled_variables",
        [],
    )

    relation_only = policy.get(
        "relation_only_variables",
        [],
    )

    overlap = (
        set(enabled)
        & set(relation_only)
    )

    if overlap:
        errors.append(
            "enabled/relation-only overlap: "
            + ", ".join(sorted(overlap))
        )

    for name in enabled:

        definition = variables.get(name)

        if definition is None:
            errors.append(
                f"{name}: missing definition"
            )
            continue

        if not definition.get(
            "source_ids"
        ):
            errors.append(
                f"{name}: missing source_ids"
            )

        if definition.get(
            "min"
        ) is None:
            errors.append(
                f"{name}: missing min"
            )

        if definition.get(
            "max"
        ) is None:
            errors.append(
                f"{name}: missing max"
            )

        if not definition.get(
            "distribution"
        ):
            errors.append(
                f"{name}: missing distribution"
            )

        if definition.get(
            "sampling_enabled"
        ) is not True:
            errors.append(
                f"{name}: sampling_enabled must be true"
            )

    for name in relation_only:

        definition = variables.get(name)

        if definition is None:
            errors.append(
                f"{name}: missing definition"
            )
            continue

        if definition.get(
            "sampling_enabled"
        ) is not False:
            errors.append(
                f"{name}: sampling_enabled must be false"
            )

        if definition.get(
            "generator_status"
        ) != "EVIDENCE_RELATION_ONLY":
            errors.append(
                f"{name}: invalid generator_status"
            )

    if policy.get(
        "require_source_for_every_sampled_variable"
    ) is not True:
        errors.append(
            "source requirement flag must be true"
        )

    if policy.get(
        "require_min_max_for_every_sampled_variable"
    ) is not True:
        errors.append(
            "min/max requirement flag must be true"
        )

    if policy.get(
        "require_relationships"
    ) is not True:
        errors.append(
            "relationship requirement flag must be true"
        )

    if policy.get(
        "require_constraints"
    ) is not True:
        errors.append(
            "constraint requirement flag must be true"
        )

    if policy.get(
        "random_seed_required"
    ) is not True:
        errors.append(
            "random seed requirement flag must be true"
        )

    if not target_policy:
        errors.append(
            "manifest.target_policy is missing"
        )

    else:

        if target_policy.get(
            "name"
        ) != "production_kg":
            errors.append(
                "target_policy.name must be production_kg"
            )

        if target_policy.get(
            "type"
        ) != "derived_target":
            errors.append(
                "production_kg must be derived_target"
            )

    return errors


def generate_synthetic_dataset(
    manifest: dict,
    rows: int = 1000,
) -> pd.DataFrame:

    if rows <= 0:
        raise ValueError(
            "rows must be greater than zero"
        )

    errors = validate_manifest(
        manifest
    )

    if errors:
        raise ValueError(
            "Generator manifest is not ready:\n"
            + "\n".join(
                f"- {error}"
                for error in errors
            )
        )

    raise NotImplementedError(
        "Synthetic generation is not implemented yet. "
        "The next milestone will implement evidence-aware "
        "correlated generation."
    )
