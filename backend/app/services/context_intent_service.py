import json

from app.ai.ollama import provider
from pydantic import BaseModel


class ContextIntentResult(BaseModel):
    intent: str
    confidence: float
    reason: str


INTENT_PROMPT = """
You are AquaLife's intent classification engine.

Choose exactly ONE intent:

general_chat
knowledge
farm_data
parameter_update
prediction
farm_advice

Definitions:

general_chat:
Casual conversation or a greeting.

knowledge:
General aquaculture information that does not require the user's own
farm data.

farm_data:
The user is providing new information about their farm, pond, species,
stocking, water quality, feeding, growth, survival, or other conditions.

parameter_update:
The user is correcting, replacing, or updating information that was
already provided earlier in the conversation.

prediction:
The user wants a numerical forecast, estimate, expected production,
growth prediction, harvest estimate, or similar prediction.

farm_advice:
The user wants advice about a specific farm or pond condition.

Use the conversation history to determine whether something is an update.

Return ONLY valid JSON:

{
  "intent": "parameter_update",
  "confidence": 0.95,
  "reason": "The user is replacing a previously stated survival value."
}
""".strip()


def classify_intent(
    text: str,
    history: list[dict[str, str]] | None = None,
) -> ContextIntentResult:

    history = history or []

    history_text = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history[-10:]
    )

    response = provider.chat(
        [
            {
                "role": "system",
                "content": INTENT_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"CONVERSATION HISTORY:\n"
                    f"{history_text or '[none]'}\n\n"
                    f"CURRENT MESSAGE:\n{text}"
                ),
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

    return ContextIntentResult.model_validate(
        json.loads(raw)
    )


if __name__ == "__main__":

    history = [
        {
            "role": "user",
            "content": "My farm grows Vannamei shrimp.",
        },
        {
            "role": "user",
            "content": "My survival rate is 82 percent.",
        },
    ]

    tests = [
        "Actually my survival is 85 percent.",
        "My pond is 2 acres.",
        "Predict my production.",
        "What is dissolved oxygen?",
    ]

    for text in tests:

        result = classify_intent(
            text,
            history=history,
        )

        print("\nINPUT:", text)
        print("INTENT:", result.intent)
        print("CONFIDENCE:", result.confidence)
        print("REASON:", result.reason)
