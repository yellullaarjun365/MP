from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timezone

from pathlib import Path

from typing import Any


BACKEND_ROOT = (
    Path(__file__).resolve().parents[2]
)

REGISTRY_ROOT = (
    BACKEND_ROOT
    / "data"
    / "external"
    / "registry"
)

DISCOVERY_ROOT = (
    REGISTRY_ROOT
    / "discovery"
)

USER_AGENT = (
    "AquaLife-Discovery/0.9.1"
)


def read_json(
    path: Path,
) -> dict[str, Any]:

    return json.loads(
        path.read_text(
            encoding="utf-8-sig"
        )
    )


def github_request(
    url: str,
) -> tuple[int, Any | None]:

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            body = response.read()

            data = json.loads(
                body.decode(
                    "utf-8"
                )
            )

            return (
                int(response.status),
                data,
            )

    except urllib.error.HTTPError as exc:

        return (
            int(exc.code),
            None,
        )

    except (
        urllib.error.URLError,
        TimeoutError,
    ):

        return (
            0,
            None,
        )


def parse_github_url(
    url: str,
) -> tuple[str | None, str | None]:

    parsed = urllib.parse.urlparse(
        url
    )

    if (
        parsed.netloc.lower()
        !=
        "github.com"
    ):

        return (
            None,
            None,
        )

    parts = [
        part
        for part in parsed.path.strip(
            "/"
        ).split("/")
        if part
    ]

    if len(parts) < 2:

        return (
            None,
            None,
        )

    owner = parts[0]

    repo = parts[1]

    if repo.endswith(
        ".git"
    ):

        repo = repo[
            :-4
        ]

    return (
        owner,
        repo,
    )


def detect_license(
    payload: dict[str, Any] | None,
) -> tuple[str, str]:

    if not payload:

        return (
            "UNKNOWN",
            "unverified",
        )

    license_data = payload.get(
        "license"
    )

    if not isinstance(
        license_data,
        dict,
    ):

        return (
            "NO_DECLARED_LICENSE",
            "unverified",
        )

    spdx_id = license_data.get(
        "spdx_id"
    )

    if spdx_id:

        return (
            str(spdx_id),
            "detected",
        )

    license_name = license_data.get(
        "name"
    )

    if license_name:

        return (
            str(license_name),
            "detected",
        )

    return (
        "UNKNOWN",
        "unverified",
    )


def decode_readme(
    payload: dict[str, Any] | None,
) -> str:

    if not payload:

        return ""

    content = payload.get(
        "content"
    )

    if not content:

        return ""

    try:

        decoded = base64.b64decode(
            content
        )

        return decoded.decode(
            "utf-8",
            errors="replace",
        )

    except (
        ValueError,
        TypeError,
    ):

        return ""


def detect_topics(
    text: str,
) -> dict[str, list[str]]:

    lower = text.lower()

    groups = {

        "water_quality": [
            "water quality",
            "dissolved oxygen",
            "oxygen forecast",
            "nitrate",
            "nitrite",
            "ammonia",
            "ph prediction",
        ],

        "production": [
            "production prediction",
            "production forecasting",
            "yield prediction",
            "yield forecasting",
            "harvest prediction",
        ],

        "growth": [
            "fish growth",
            "growth prediction",
            "growth rate",
            "biomass",
            "weight prediction",
        ],

        "disease": [
            "disease detection",
            "disease prediction",
            "early disease",
            "health classification",
        ],

        "computer_vision": [
            "computer vision",
            "object detection",
            "segmentation",
            "mask r-cnn",
        ],

        "digital_twin": [
            "digital twin",
            "state estimation",
            "physics informed",
        ],

        "federated_learning": [
            "federated learning",
        ],
    }

    result: dict[str, list[str]] = {}

    for group, keywords in groups.items():

        matches = [
            keyword
            for keyword in keywords
            if keyword in lower
        ]

        if matches:

            result[group] = matches

    return result


def detect_frameworks(
    text: str,
) -> list[str]:

    lower = text.lower()

    frameworks = [
        "catboost",
        "xgboost",
        "random forest",
        "svr",
        "lstm",
        "bilstm",
        "bigru",
        "gru",
        "tcn",
        "transformer",
        "patchtst",
        "mamba",
        "cnn",
        "pytorch",
        "tensorflow",
        "keras",
        "scikit-learn",
    ]

    return [
        framework
        for framework in frameworks
        if framework in lower
    ]


def discover_repository(
    source: dict[str, Any],
) -> dict[str, Any]:

    url = source[
        "url"
    ]

    owner, repo = parse_github_url(
        url
    )

    result: dict[str, Any] = {

        "source_id":
            source[
                "source_id"
            ],

        "name":
            source[
                "name"
            ],

        "url":
            url,

        "source_type":
            source.get(
                "type"
            ),

        "retrieved_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "http_status":
            None,

        "repository_exists":
            False,

        "readme_available":
            False,

        "readme_length":
            0,

        "license":
            "UNKNOWN",

        "license_status":
            "unverified",

        "default_branch":
            None,

        "stars":
            None,

        "forks":
            None,

        "open_issues":
            None,

        "last_push":
            None,

        "topic_matches":
            {},

        "frameworks":
            [],

        "candidate_resource_types":
            [],

        "discovery_status":
            "FAILED",

        "notes":
            [],
    }


    if not owner or not repo:

        result[
            "notes"
        ].append(
            "Invalid GitHub URL."
        )

        return result


    repository_url = (
        "https://api.github.com/repos/"
        + owner
        + "/"
        + repo
    )


    status, repository = github_request(
        repository_url
    )


    result[
        "http_status"
    ] = status


    if (
        status != 200
        or not isinstance(
            repository,
            dict,
        )
    ):

        result[
            "notes"
        ].append(
            "Repository metadata unavailable."
        )

        return result


    result[
        "repository_exists"
    ] = True


    result[
        "default_branch"
    ] = repository.get(
        "default_branch"
    )

    result[
        "stars"
    ] = repository.get(
        "stargazers_count"
    )

    result[
        "forks"
    ] = repository.get(
        "forks_count"
    )

    result[
        "open_issues"
    ] = repository.get(
        "open_issues_count"
    )

    result[
        "last_push"
    ] = repository.get(
        "pushed_at"
    )


    license_name, license_status = (
        detect_license(
            repository
        )
    )


    result[
        "license"
    ] = license_name

    result[
        "license_status"
    ] = license_status


    readme_url = (
        repository_url
        + "/readme"
    )


    readme_status, readme_payload = (
        github_request(
            readme_url
        )
    )


    readme_text = decode_readme(
        readme_payload
    )


    if readme_text:

        result[
            "readme_available"
        ] = True

        result[
            "readme_length"
        ] = len(
            readme_text
        )


    combined_text = (
        readme_text
        + "\n"
        + json.dumps(
            repository
        )
    )


    topics = detect_topics(
        combined_text
    )

    frameworks = detect_frameworks(
        combined_text
    )


    result[
        "topic_matches"
    ] = topics

    result[
        "frameworks"
    ] = frameworks


    candidate_types = []


    for resource_type in [
        "water_quality",
        "production",
        "growth",
        "disease",
        "computer_vision",
        "digital_twin",
        "federated_learning",
    ]:

        if resource_type in topics:

            candidate_types.append(
                resource_type
            )


    result[
        "candidate_resource_types"
    ] = sorted(
        set(
            candidate_types
        )
    )


    if result[
        "readme_available"
    ]:

        result[
            "discovery_status"
        ] = "DISCOVERED"

    else:

        result[
            "discovery_status"
        ] = "PARTIAL"


    if result[
        "license_status"
    ] != "detected":

        result[
            "notes"
        ].append(
            "License requires manual verification."
        )


    return result


def run_discovery() -> dict[str, Any]:

    source_file = (
        DISCOVERY_ROOT
        / "sources.json"
    )


    source_registry = read_json(
        source_file
    )


    sources = source_registry.get(
        "sources",
        []
    )


    results = []


    for source in sources:

        source_type = source.get(
            "type"
        )

        if (
            source_type
            ==
            "github_repository"
        ):

            result = discover_repository(
                source
            )

        else:

            result = {
                "source_id":
                    source.get(
                        "source_id"
                    ),

                "name":
                    source.get(
                        "name"
                    ),

                "url":
                    source.get(
                        "url"
                    ),

                "source_type":
                    source_type,

                "discovery_status":
                    "UNSUPPORTED_SOURCE_TYPE",

                "notes": [
                    "Unsupported source type."
                ],
            }


        results.append(
            result
        )


    output = (
        DISCOVERY_ROOT
        / "discovery-results.json"
    )


    payload = {

        "schema_version":
            "aqualife-discovery-results-v1",

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "source_count":
            len(results),

        "results":
            results,
    }


    DISCOVERY_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )


    output.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )


    return payload
