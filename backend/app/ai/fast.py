from app.ai.ollama import OllamaError, provider


def fast_chat(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
) -> str:
    return provider.chat(
        messages,
        temperature=temperature,
        think=False,
    )


print("Fast chat helper imported successfully")
