
from __future__ import annotations

import json

from pathlib import Path

from app.model_worker.schemas.manifest import (
    ApprovedResource,
)


ROOT = Path.cwd()

MANIFEST_DIR = (
    ROOT
    / "data"
    / "external"
    / "sandbox"
    / "worker"
    / "manifests"
)


def load_manifest(
    resource_id: str,
) -> ApprovedResource:

    path = (
        MANIFEST_DIR
        / f"{resource_id}.json"
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Worker approval manifest not found: {path}"
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )

    return ApprovedResource.model_validate(
        payload
    )


def validate_approval(
    resource: ApprovedResource,
) -> None:

    if not resource.approved_for_execution:

        raise PermissionError(
            "Resource is not approved for execution."
        )

    if not resource.license_verified:

        raise PermissionError(
            "Resource license is not verified."
        )

    if not resource.artifact_sha256:

        raise PermissionError(
            "Resource artifact hash is missing."
        )

    if not resource.source_url:

        raise PermissionError(
            "Resource source URL is missing."
        )

    if not resource.artifact_path:

        raise PermissionError(
            "Resource artifact path is missing."
        )
