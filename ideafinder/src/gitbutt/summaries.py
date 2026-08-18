"""DeepSeek V4 Flash summaries for the repo pool.

One API call per batch of repos; strict JSON output; results land in
repo_summaries. Skips repos that already have a summary, so reruns are cheap.
"""

from __future__ import annotations

import json
import re

import httpx

from gitbutt.db import connect
from gitbutt.deepseek import chat, load_env

BATCH_SIZE = 25

README_URLS = (
    "https://raw.githubusercontent.com/{full}/HEAD/README.md",
    "https://raw.githubusercontent.com/{full}/HEAD/readme.md",
    "https://raw.githubusercontent.com/{full}/HEAD/README.rst",
)

SUMMARY_PROMPT = """You are a repo researcher. Below are GitHub repository names featured on a YouTube channel that covers trending open source projects, each with the video it appeared in and an excerpt of its README when available. For every repo, write one or two plain-English sentences on what the project is and who it is for, plus 2 to 4 short tags. Base your answer on the README excerpt and the video context. Never invent specific claims you cannot know.

Return ONLY a JSON object, no prose, shaped exactly like:
{"owner/repo": {"summary": "...", "tags": ["tag1", "tag2"]}}

Repos:
{repos}
"""


def _readme_excerpt(full_name: str, max_chars: int = 1500) -> str:
    """First chunk of the repo README, or "" when unavailable."""
    for url_template in README_URLS:
        try:
            resp = httpx.get(
                url_template.format(full=full_name), timeout=15, follow_redirects=True
            )
            if resp.status_code != 200:
                continue
            return re.sub(r"\s+", " ", resp.text)[:max_chars]
        except httpx.HTTPError:
            continue
    return ""


def _call(repos_block: str, timeout: float = 180.0) -> dict:
    return chat(SUMMARY_PROMPT.replace("{repos}", repos_block), max_tokens=8000, timeout=timeout)

def summarize_missing(limit: int | None = None, batch_size: int = BATCH_SIZE) -> dict:
    """Summarize repos without a summary yet. Returns counts; never raises on API errors.
    No DB connection is held during API calls, so concurrent jobs never wait on a lock."""
    load_env()
    conn = connect()
    try:
        rows = conn.execute(
            """SELECT r.full_name, v.title AS video_title
               FROM repos r
               LEFT JOIN videos v ON v.video_id = r.first_seen_video
               WHERE r.full_name NOT IN (SELECT full_name FROM repo_summaries)
               ORDER BY r.full_name"""
        ).fetchall()
        if limit:
            rows = rows[:limit]
    finally:
        conn.close()

    total = 0
    failed: list[str] = []
    for i in range(0, len(rows), batch_size):
        chunk = rows[i : i + batch_size]
        lines = []
        for r in chunk:
            excerpt = _readme_excerpt(r["full_name"])
            line = f"- {r['full_name']} (video: {r['video_title'] or 'unknown'})"
            if excerpt:
                line += f"\n  README: {excerpt}"
            lines.append(line)
        block = "\n".join(lines)
        try:
            result = _call(block)
        except (httpx.HTTPError, ValueError, KeyError):
            failed.extend(r["full_name"] for r in chunk)
            continue
        write_conn = connect()
        try:
            for r in chunk:
                item = result.get(r["full_name"])
                if not isinstance(item, dict) or not item.get("summary"):
                    failed.append(r["full_name"])
                    continue
                write_conn.execute(
                    "INSERT OR REPLACE INTO repo_summaries (full_name, summary, tags) VALUES (?, ?, ?)",
                    (r["full_name"], item["summary"].strip(), json.dumps(item.get("tags", []))),
                )
                total += 1
            write_conn.commit()
        finally:
            write_conn.close()
    return {"attempted": len(rows), "summarized": total, "failed": failed}
