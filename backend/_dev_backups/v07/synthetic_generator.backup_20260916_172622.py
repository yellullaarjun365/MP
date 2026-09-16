from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]


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

    policy = manifest.get(
        "generator_policy"
    )

    if not policy:

        errors.append(
            "generator_policy is missing"
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

    variables = manifest.get(
        "variables",
        {},
    )

    # --------------------------------------------------------
    # Check for overlap.
    # --------------------------------------------------------

    overlap =
        set(enabled)
        &
        set(relation_only)

    if overlap:

        errors.append(
            "Variables cannot be both enabled "
            f"and relation-only: {sorted(overlap)}"
        )

    # --------------------------------------------------------
    # Validate sampleable variables.
    # --------------------------------------------------------

    for name in enabled:

        definition = variables.get(
            name
        )

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

        if definition.get(
            "distribution"
        ) is None:

            errors.append(
                f"{name}: missing distribution"
            )

        if definition.get(
            "sampling_enabled"
        ) is not True:

            errors.append(
                f"{name}: sampling_enabled "
                "must be true"
            )

    # --------------------------------------------------------
    # Validate relation-only variables.
    # --------------------------------------------------------

    for name in relation_only:

        definition = variables.get(
            name
        )

        if definition is None:

            errors.append(
                f"{name}: missing definition"
            )

            continue

        if definition.get(
            "sampling_enabled"
        ) is not False:

            errors.append(
                f"{name}: sampling_enabled "
                "must be false"
            )

        if definition.get(
            "generator_status"
        ) != "EVIDENCE_RELATION_ONLY":

            errors.append(
                f"{name}: incorrect "
                "generator_status"
            )

    # --------------------------------------------------------
    # Validate required policy flags.
    # --------------------------------------------------------

    required_flags = [
        "require_source_for_every_sampled_variable",
        "require_min_max_for_every_sampled_variable",
        "require_relationships",
        "require_constraints",
        "random_seed_required",
    ]

    for flag in required_flags:

        if policy.get(flag) is not True:

            errors.append(
                f"generator_policy.{flag} "
                "must be true"
            )

    # --------------------------------------------------------
    # Evidence.
    # --------------------------------------------------------

    if not manifest.get(
        "sources"
    ):

        errors.append(
            "Evidence sources are missing"
        )

    # --------------------------------------------------------
    # Relationships.
    # --------------------------------------------------------

    if policy.get(
        "require_relationships"
    ):

        if not manifest.get(
            "relationships"
        ):

            errors.append(
                "Relationships are required"
            )

    # --------------------------------------------------------
    # Constraints.
    # --------------------------------------------------------

    if policy.get(
        "require_constraints"
    ):

        if not manifest.get(
            "constraints"
        ):

            errors.append(
                "Constraints are required"
            )

    # --------------------------------------------------------
    # Target.
    # --------------------------------------------------------

    target_policy =
        manifest.get(
            "target_policy"
        )

    if not target_policy:

        errors.append(
            "target_policy is missing"
        )

    else:

        if target_policy.get(
            "name"
        ) != "production_kg":

            errors.append(
                "Prediction target must be "
                "production_kg"
            )

        if target_policy.get(
            "type"
        ) != "derived_target":

            errors.append(
                "production_kg must be "
                "a derived target"
            )

    return errors
