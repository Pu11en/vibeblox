"""Shared DeepSeek API client helpers for all GITBUTT agents."""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-v4-flash"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_env() -> None:
    """Fallback: read the project .env when the key is not in the environment."""
    if os.environ.get("DEEPSEEK_API_KEY"):
        return
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def auth_headers() -> dict[str, str]:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def parse_json(content: str) -> dict[str, Any]:
    content = content.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", content, re.DOTALL)
    if fence:
        content = fence.group(1).strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Tolerate prose wrapped around the JSON object.
        obj = re.search(r"\{.*\}", content, re.DOTALL)
        if obj:
            return json.loads(obj.group(0))
        raise


def chat(prompt: str, max_tokens: int = 8000, timeout: float = 180.0, retries: int = 3) -> dict[str, Any]:
    """One DeepSeek V4 Flash call returning parsed JSON. Retries transient
    failures with backoff. DeepSeek V4 Flash is a reasoning model, so keep
    max_tokens generous: reasoning tokens count against the budget."""
    load_env()
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            resp = httpx.post(API_URL, headers=auth_headers(), json=payload, timeout=timeout)
            resp.raise_for_status()
            return parse_json(resp.json()["choices"][0]["message"]["content"])
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
    raise last_error  # type: ignore[misc]
