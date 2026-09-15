import json
from enum import Enum

from app.ai.ollama import provider
from pydantic import BaseModel


class UserIntent(str, Enum):
    GENERAL_CHAT = "general_chat"
    KNOWLEDGE = "knowledge"
    FARM_DATA = "farm_data"
    PARAMETER_UPDATE = "parameter_update"
    PREDICTION = "prediction"
    FARM_ADVICE = "farm_advice"


class IntentResult(BaseModel):
    intent: UserIntent
    confidence: float
    reason: str


INTENT_PROMPT = """
You are AquaLife's intent classification engine.

Classify the user's message into EXACTLY ONE intent.

Allowed intents:

general_chat
knowledge
farm_data
parameter_update
prediction
farm_advice

Definitions:

general_chat:
Casual conversation or requests unrelated to a specific aquaculture
knowledge question or farm operation.

knowledge:
A general aquaculture knowledge question that does not depend on the
user's own farm.

farm_data:
The user is explicitly providing information about their farm, pond,
species, stocking, water quality, feeding, growth, survival, or other
farm conditions.

parameter_update:
The user is changing or correcting information previously supplied.

prediction:
The user wants a forecast, prediction, estimate, expected production,
harvest estimate, growth forecast, or similar numerical prediction.

farm_advice:
The user wants advice or an action recommendation for their specific
farm or pond.

Return ONLY valid JSON:

{
  "intent": "knowledge",
  "confidence": 0.95,
  "reason": "..."
}

Rules:
- Do not invent facts.
- Choose only one intent.
- confidence must be between 0 and 1.
- Keep reason short.
- Return JSON only.
""".strip()


def classify_intent(
    text: str,
) -> IntentResult:

    response = provider.chat(
        [
            {
                "role": "system",
                "content": INTENT_PROMPT,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.0,
        think=False,
    )

    raw = response.strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "")
        raw = raw.replace("```", "")
        raw = raw.strip("` \n")

    return IntentResult.model_validate(
        json.loads(raw)
    )


if __name__ == "__main__":

    tests = [
        "What is dissolved oxygen?",
        "My pond is 2 acres and I stocked 20000 Vannamei.",
        "Actually my survival is 85 percent.",
        "Predict my shrimp production.",
        "What should I do if my pond oxygen is low?",
        "Tell me about shrimp feeding.",
        "Hello Aqua AI.",
    ]

    for test in tests:

        result = classify_intent(test)

        print("\nINPUT:")
        print(test)

        print(
            "INTENT:",
            result.intent.value,
        )

        print(
            "CONFIDENCE:",
            result.confidence,
        )

        print(
            "REASON:",
            result.reason,
        )
