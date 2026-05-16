from __future__ import annotations

import json
import os
import re
import ssl
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi


@dataclass
class GroqConfig:
    enabled: bool
    api_key: str | None
    model: str
    base_url: str
    timeout_seconds: float


def load_groq_config() -> GroqConfig:
    enabled = os.getenv("GROQ_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    return GroqConfig(
        enabled=enabled,
        api_key=os.getenv("GROQ_API_KEY"),
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1/chat/completions"),
        timeout_seconds=float(os.getenv("GROQ_TIMEOUT_SECONDS", "25")),
    )


def groq_available() -> bool:
    config = load_groq_config()
    return config.enabled and bool(config.api_key)


def groq_status() -> tuple[bool, str]:
    config = load_groq_config()
    if not config.enabled:
        return False, "AI review is disabled in backend/.env"
    if not config.api_key:
        return False, "AI review is enabled but GROQ_API_KEY is missing"
    return True, f"AI review ready with model {config.model}"


def chat_json(*, system_prompt: str, user_prompt: str) -> tuple[dict | None, str | None]:
    config = load_groq_config()
    if not config.enabled:
        return None, "Groq AI is disabled"
    if not config.api_key:
        return None, "Groq API key is missing"

    payload = {
        "model": config.model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    request = Request(
        config.base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DegreeBaba-App/1.0 (Python)",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=config.timeout_seconds, context=_ssl_context()) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="ignore")
        return None, f"Groq HTTP error {error.code}: {detail[:300]}"
    except URLError as error:
        return None, f"Groq connection error: {error.reason}"
    except Exception as error:  # pragma: no cover - defensive
        return None, f"Groq request failed: {error}"

    content = (
        body.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    if not content:
        return None, "Groq returned an empty response"

    cleaned = _strip_code_fence(content)
    try:
        return json.loads(cleaned), None
    except json.JSONDecodeError:
        return None, f"Groq returned invalid JSON: {cleaned[:300]}"


def _strip_code_fence(content: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", content, re.S)
    if match:
        return match.group(1).strip()
    return content.strip()


def _ssl_context():
    cafile = os.getenv("GROQ_CA_BUNDLE") or certifi.where()
    return ssl.create_default_context(cafile=cafile)
