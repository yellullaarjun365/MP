from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BACKEND_ROOT = (
    Path(__file__).resolve().parents[2]
)

DISCOVERY_ROOT = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "registry"
    / "discovery"
)


def load_discovery_results() -> dict[str, Any]:

    path = (
        DISCOVERY_ROOT
        / "discovery-results.json"
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Discovery results not found: {path}"
        )

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )
