"""DeepSeek (OpenAI-compatible) call with JSON output + cost tracking.

Same pattern as the proven Blotato bridge: plain urllib, no dependencies.
"""
import json
import os
import time
import urllib.request

BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
# USD per 1M tokens (cache-miss input / output), official pricing 2026.
IN_RATE = float(os.environ.get("DEEPSEEK_IN_RATE", "0.14"))
OUT_RATE = float(os.environ.get("DEEPSEEK_OUT_RATE", "0.28"))


def json_call(system, user, max_tokens=8000, extra=None, timeout=300):
    """Call the brain. Returns (parsed_json_dict, cost_usd). Raises on failure."""
    if not API_KEY:
        raise RuntimeError("no DeepSeek API key — put DEEPSEEK_API_KEY in backend/.env")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    if extra:
        messages.append({"role": "user", "content": "Extra info: " + json.dumps(extra)})
    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.4,
    }).encode()
    req = urllib.request.Request(f"{BASE}/chat/completions", data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"brain API error {e.code}: {detail}") from e
    content = data["choices"][0]["message"]["content"].strip()
    # tolerate markdown fences around the JSON
    if content.startswith("```"):
        content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    parsed = json.loads(content)  # raises json.JSONDecodeError -> caller retries
    usage = data.get("usage", {})
    tin = int(usage.get("prompt_tokens", 0))
    tout = int(usage.get("completion_tokens", 0))
    cost = tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE
    print(f"[p2b] llm {tin}+{tout} tok ~${cost:.4f} in {time.time()-t0:.1f}s", flush=True)
    return parsed, cost
