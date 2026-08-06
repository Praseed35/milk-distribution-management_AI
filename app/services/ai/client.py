import httpx

from app.core.config import (
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_MODEL,
    AI_ENABLED,
    AI_LLM_DISABLED,
)
from app.exceptions.ai import AIUnavailableError


def is_available() -> bool:
    if not AI_ENABLED or AI_LLM_DISABLED:
        return False
    if not NVIDIA_API_KEY:
        return False
    return True


def chat_completion(messages: list[dict], max_tokens: int | None = None) -> str:
    payload: dict = {
        "model": NVIDIA_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    try:
        response = httpx.post(
            f"{NVIDIA_BASE_URL.rstrip('/')}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            timeout=30,
        )
    except httpx.HTTPError as e:
        raise AIUnavailableError(str(e)) from e

    if response.status_code != 200:
        raise AIUnavailableError(
            f"AI service returned HTTP {response.status_code}"
        )

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise AIUnavailableError("AI service returned an unexpected response") from e
