
from __future__ import annotations

import json
import sys


def main() -> int:

    raw = sys.stdin.read()

    if not raw:

        print(
            json.dumps(
                {
                    "status": "FAILED",
                    "reason": "empty_request",
                }
            )
        )

        return 1


    try:

        request = json.loads(
            raw
        )

    except json.JSONDecodeError:

        print(
            json.dumps(
                {
                    "status": "FAILED",
                    "reason": "invalid_json",
                }
            )
        )

        return 1


    # Deliberately no dynamic imports,
    # no shell execution,
    # no network access,
    # and no model loading.
    #
    # This worker image is a controlled foundation.
    # The next phase can inject a specifically
    # approved adapter.

    response = {

        "status": "READY",

        "execution": "DISABLED",

        "resource_id":
            request.get(
                "resource_id"
            ),

        "task":
            request.get(
                "task"
            ),

        "third_party_code_executed":
            False,

        "model_weights_loaded":
            False,

        "notes": [
            "Worker reached successfully.",
            "Third-party execution is disabled.",
        ],
    }


    print(
        json.dumps(
            response
        )
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
