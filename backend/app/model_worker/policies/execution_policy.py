
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkerSecurityPolicy(BaseModel):

    network_enabled: bool = False

    privileged: bool = False

    host_source_mounts: bool = False

    host_model_mounts: bool = False

    read_only_rootfs: bool = True

    allow_package_install_at_runtime: bool = False

    allow_shell: bool = False

    allow_training: bool = False

    allow_deployment: bool = False

    cpu_limit: float = 1.0

    memory_limit_mb: int = 1024

    execution_timeout_seconds: int = 120

    max_output_bytes: int = 5_000_000

    allowed_frameworks: list[str] = Field(
        default_factory=list
    )


DEFAULT_POLICY = WorkerSecurityPolicy()


def validate_policy(
    policy: WorkerSecurityPolicy,
) -> list[str]:

    violations = []

    if policy.network_enabled:
        violations.append(
            "network_enabled must be false"
        )

    if policy.privileged:
        violations.append(
            "privileged must be false"
        )

    if policy.host_source_mounts:
        violations.append(
            "host_source_mounts must be false"
        )

    if policy.host_model_mounts:
        violations.append(
            "host_model_mounts must be false"
        )

    if not policy.read_only_rootfs:
        violations.append(
            "read_only_rootfs must be true"
        )

    if policy.allow_package_install_at_runtime:
        violations.append(
            "runtime package installation is disabled"
        )

    if policy.allow_shell:
        violations.append(
            "shell execution is disabled"
        )

    if policy.allow_training:
        violations.append(
            "automatic training is disabled"
        )

    if policy.allow_deployment:
        violations.append(
            "automatic deployment is disabled"
        )

    if policy.cpu_limit <= 0:
        violations.append(
            "cpu_limit must be positive"
        )

    if policy.memory_limit_mb <= 0:
        violations.append(
            "memory_limit_mb must be positive"
        )

    if policy.execution_timeout_seconds <= 0:
        violations.append(
            "execution timeout must be positive"
        )

    return violations
