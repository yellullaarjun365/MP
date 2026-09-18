
from __future__ import annotations

import json

from pathlib import Path

from app.prediction.adapters.external_spec import (
    ExternalAdapterSpec,
)


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "data"
    / "external"
    / "sandbox"
    / "reports"
    / "sandbox-results.json"
)


def build_external_adapter_specs(
    payload: dict,
) -> list[ExternalAdapterSpec]:

    specs = []

    for item in payload.get(
        "results",
        [],
    ):

        source_id = str(
            item.get(
                "source_id",
                "unknown",
            )
        )

        slug = source_id.lower()

        slug = slug.replace(
            "-",
            "_",
        )

        tasks = [
            str(x)
            for x in item.get(
                "candidate_tasks",
                [],
            )
        ]

        frameworks = [
            str(x)
            for x in item.get(
                "frameworks",
                [],
            )
        ]

        features = []

        for values in item.get(
            "candidate_features",
            {},
        ).values():

            if isinstance(
                values,
                list,
            ):

                features.extend(
                    str(x)
                    for x in values
                )


        features = sorted(
            set(features)
        )


        artifact_count = (
            len(
                item.get(
                    "model_artifacts",
                    [],
                )
            )
        )


        license_verified = (
            item.get(
                "license_status"
            )
            ==
            "detected"
        )


        repository_available = (
            item.get(
                "repository_status"
            )
            ==
            "AVAILABLE"
        )


        archive_hash = item.get(
            "archive_sha256"
        )


        benchmark_allowed = (
            repository_available
            and
            license_verified
            and
            artifact_count > 0
            and
            bool(tasks)
            and
            False
        )


        notes = [
            "Adapter is metadata-only.",
            "Third-party code execution is disabled.",
            "Third-party weights are not loaded.",
        ]


        if not license_verified:

            notes.append(
                "Manual license verification required."
            )


        if artifact_count == 0:

            notes.append(
                "No recognized pretrained model artifact."
            )


        for task in (
            tasks
            or ["unknown"]
        ):

            task_slug = re_slug(
                task
            )

            adapter_id = (
                "external_"
                + slug
                + "_"
                + task_slug
            )


            model_id = (
                "external:"
                + source_id
                + ":"
                + task
            )


            specs.append(
                ExternalAdapterSpec(
                    adapter_id=adapter_id,
                    model_id=model_id,
                    source_id=source_id,
                    source_url=str(
                        item.get(
                            "url",
                            "",
                        )
                    ),
                    task=task,
                    framework=frameworks,
                    candidate_features=features,
                    license=str(
                        item.get(
                            "license",
                            "UNKNOWN",
                        )
                    ),
                    license_verified=license_verified,
                    artifact_available=(
                        artifact_count > 0
                    ),
                    artifact_count=artifact_count,
                    repository_available=repository_available,
                    archive_sha256=archive_hash,
                    execution_allowed=False,
                    weights_loaded=False,
                    benchmark_allowed=benchmark_allowed,
                    approval_status="NOT_APPROVED",
                    notes=notes,
                )
            )


    return specs


def re_slug(
    value: str,
) -> str:

    result = value.lower()

    result = result.replace(
        "-",
        "_",
    )

    result = result.replace(
        " ",
        "_",
    )

    result = (
        "".join(
            character
            for character in result
            if character.isalnum()
            or character == "_"
        )
    )

    return (
        result[:80]
        or "unknown"
    )


def load_specs() -> list[
    ExternalAdapterSpec
]:

    payload = json.loads(
        REPORT.read_text(
            encoding="utf-8-sig"
        )
    )

    return build_external_adapter_specs(
        payload
    )
