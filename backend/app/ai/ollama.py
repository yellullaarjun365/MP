import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b",
)


class OllamaError(RuntimeError):
    pass


class OllamaProvider:
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def health(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.base_url}/api/tags"
                )

            response.raise_for_status()

            payload = response.json()

            models = [
                item.get("name")
                for item in payload.get("models", [])
            ]

            return {
                "available": True,
                "model": self.model,
                "model_installed": self.model in models,
                "base_url": self.base_url,
            }

        except Exception as exc:
            return {
                "available": False,
                "model": self.model,
                "model_installed": False,
                "base_url": self.base_url,
                "error": str(exc),
            }

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            with httpx.Client(
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=180.0,
                    write=30.0,
                    pool=10.0,
                )
            ) as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )

            response.raise_for_status()

            data = response.json()

            content = (
                data.get("message", {})
                .get("content", "")
                .strip()
            )

            if not content:
                raise OllamaError(
                    "Ollama returned an empty response."
                )

            return content

        except httpx.HTTPStatusError as exc:
            raise OllamaError(
                f"Ollama HTTP error {exc.response.status_code}: "
                f"{exc.response.text}"
            ) from exc

        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Could not connect to Ollama: {exc}"
            ) from exc


provider = OllamaProvider()
