
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time

from pathlib import Path
from typing import Any

from app.model_worker.policies.execution_policy import (
    DEFAULT_POLICY,
    validate_policy,
)

from app.model_worker.runtime.approval import (
    load_manifest,
    validate_approval,
)

from app.model_worker.schemas.manifest import (
    WorkerRequest,
    WorkerResult,
)


ROOT = Path.cwd()

RESULT_DIR = (
    ROOT
    / "data"
    / "external"
    / "sandbox"
    / "worker"
    / "results"
)


def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:

        while True:

            block = handle.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(
                block
            )

    return digest.hexdigest()


def execute_request(
    request: WorkerRequest,
) -> WorkerResult:

    policy_errors = validate_policy(
        DEFAULT_POLICY
    )

    if policy_errors:

        return WorkerResult(
            resource_id=request.resource_id,
            task=request.task,
            status="REJECTED",
            execution_status="POLICY_REJECTED",
            notes=policy_errors,
        )


    try:

        manifest = load_manifest(
            request.resource_id
        )

        validate_approval(
            manifest
        )

    except FileNotFoundError as exc:

        return WorkerResult(
            resource_id=request.resource_id,
            task=request.task,
            status="REJECTED",
            execution_status="MANIFEST_NOT_FOUND",
            notes=[str(exc)],
        )

    except PermissionError as exc:

        return WorkerResult(
            resource_id=request.resource_id,
            task=request.task,
            status="REJECTED",
            execution_status="NOT_APPROVED",
            notes=[str(exc)],
        )


    if manifest.task != request.task:

        return WorkerResult(
            resource_id=request.resource_id,
            task=request.task,
            status="REJECTED",
            execution_status="TASK_MISMATCH",
            artifact_sha256=manifest.artifact_sha256,
            notes=[
                "Requested task does not match approval manifest."
            ],
        )


    artifact = Path(
        manifest.artifact_path
    )


    if not artifact.exists():

        return WorkerResult(
            resource_id=request.resource_id,
            task=request.task,
            status="REJECTED",
            execution_status="ARTIFACT_NOT_FOUND",
            artifact_sha256=manifest.artifact_sha256,
            notes=[
                "Approved artifact is not present."
            ],
        )


    actual_hash = sha256_file(
        artifact
    )


    if actual_hash != manifest.artifact_sha256:

        return WorkerResult(
            resource_id=request.resource_id,
            task=request.task,
            status="REJECTED",
            execution_status="HASH_MISMATCH",
            artifact_sha256=actual_hash,
            notes=[
                "Artifact hash differs from approval manifest."
            ],
        )


    return WorkerResult(
        resource_id=request.resource_id,
        task=request.task,
        status="READY",
        execution_status="EXECUTION_NOT_ENABLED",
        artifact_sha256=actual_hash,
        notes=[
            "Artifact identity verified.",
            "Approval verified.",
            "Task verified.",
            "Third-party inference execution remains disabled "
            "until the Docker worker is explicitly enabled.",
        ],
    )
