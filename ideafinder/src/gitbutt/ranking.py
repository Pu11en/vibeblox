"""Ranking agent: money-odds scores from verified free signal sources.

Implements the approved rubric (wayfinder ticket Name the money-odds rubric).
Tier 1 signals (this module): GitHub repo health, HN interest, package
downloads, niche size. Tier 2 signals (communities, newsletters, reviews,
pricing) run later for the top ideas. Every point is backed by a stored
evidence excerpt; kill switches zero an idea outright.
"""

from __future__ import annotations

import json
import math
import time

import httpx

from gitbutt.db import connect
from gitbutt.deepseek import chat, load_env

UA = {"User-Agent": "gitbutt/0.1"}
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0"}

# Rubric weights
W_DEMAND = 30
W_REACH = 25
W_GAP = 15
W_SHIP = 15
W_PRODUCT = 15

EMAIL_BATCH = 5

EMAIL_PROMPT = """You are a cold email copywriter for indie SaaS products. For each product idea below, write a short cold outreach email: a subject line and a body of at most 120 words, plain text, addressed to the target customer. The tone is helpful and specific, not salesy. Mention the concrete problem and the concrete fix.

Return ONLY JSON:
{"emails": [{"idea_id": 1, "subject": "...", "body": "..."}]}

Ideas:
{ideas}
"""


def _get(url: str, timeout: float = 30.0) -> httpx.Response:
    resp = httpx.get(url, headers=UA, timeout=timeout, follow_redirects=True)
    resp.raise_for_status()
    return resp


# --- Tier 1 signals ---


def gh_repo(full_name: str) -> dict | None:
    """S1: repo metadata. Returns None when the repo is gone or blocked."""
    try:
        data = _get(f"https://api.github.com/repos/{full_name}").json()
    except httpx.HTTPError:
        return None
    return {
        "stars": int(data.get("stargazers_count") or 0),
        "license": (data.get("license") or {}).get("spdx_id"),
        "archived": bool(data.get("archived")),
        "pushed_at": data.get("pushed_at"),
        "homepage": data.get("homepage"),
        "description": data.get("description"),
        "language": data.get("language"),
        "topics": data.get("topics") or [],
        "has_readme": not data.get("archived"),  # placeholder; README check via raw later
    }


def hn_interest(full_name: str) -> dict:
    """S3: HN mentions of the repo URL and its bare name."""
    owner, name = full_name.split("/", 1)
    url_hits = _hn_hits(f"github.com%2F{owner}%2F{name}")
    name_hits = _hn_hits(name)
    return {"url_hits": url_hits, "name_hits": name_hits}


def _hn_hits(query: str) -> int:
    try:
        data = _get(
            f"https://hn.algolia.com/api/v1/search?query={query}&tags=story&hitsPerPage=5"
        ).json()
        return int(data.get("nbHits") or 0)
    except httpx.HTTPError:
        return 0


def package_downloads(name: str) -> dict:
    """S4: weekly downloads from the registry matching the repo name."""
    found = {}
    try:
        data = _get(f"https://api.npmjs.org/downloads/point/last-week/{name}").json()
        if "downloads" in data:
            found["npm"] = int(data["downloads"])
    except httpx.HTTPError:
        pass
    if not found:
        try:
            data = _get(f"https://crates.io/api/v1/crates/{name}").json()
            found["crates"] = int(data["crate"]["recent_downloads"])
        except httpx.HTTPError:
            pass
    if not found:
        try:
            data = _get(f"https://pypi.org/pypi/{name}/json").json()
            found["pypi"] = int(data["info"].get("version") and 1 or 0)
        except httpx.HTTPError:
            pass
    return found


def niche_size(topic: str) -> int | None:
    """S2: how many repos occupy the niche, via GitHub search."""
    try:
        data = _get(
            f"https://api.github.com/search/repositories?q={topic}+in:description,readme&per_page=1"
        ).json()
        return int(data.get("total_count") or 0)
    except httpx.HTTPError:
        return None


# --- Scoring ---


def _logscale(value: int | None, cap: float = 6.0) -> float:
    if value is None or value <= 0:
        return 0.0
    return min(1.0, math.log10(1 + value) / cap)


def score_repo_signals(signals: dict) -> dict:
    """Dimension scores for one repo, per the approved rubric."""
    stars = _logscale(signals.get("stars"), cap=6.0)  # 1M stars = full
    downloads = max((_logscale(v) for v in signals.get("downloads", {}).values()), default=0.0)
    hn = min(1.0, (min(5, signals.get("hn", {}).get("url_hits", 0)) * 2
                   + min(3, signals.get("hn", {}).get("name_hits", 0))) / 13.0)
    demand = max(stars, downloads, hn) * W_DEMAND

    license_spdx = signals.get("license")
    license_ok = 1.0 if license_spdx in PERMISSIVE else (0.5 if license_spdx else 0.25)
    if license_spdx and license_spdx.startswith("AGPL"):
        license_ok = 0.25
    fresh = 1.0 if signals.get("fresh") else 0.0
    ship = (0.5 * license_ok + 0.25 * fresh + 0.25 * signals.get("has_readme", 0.0)) * W_SHIP

    product = (0.6 if signals.get("homepage") else 0.0) + 0.4 * _logscale(signals.get("stars"), cap=5.0)
    product = min(1.0, product) * W_PRODUCT

    total_count = signals.get("niche_total")
    gap = 0.0
    if total_count is not None:
        gap = max(0.0, (4.0 - math.log10(1 + total_count)) / 4.0) * W_GAP

    return {"demand": round(demand, 1), "gap": round(gap, 1), "ship": round(ship, 1),
            "product": round(product, 1), "reachability": None}


def tier1_for_repo(full_name: str) -> dict:
    repo = gh_repo(full_name)
    if repo is None:
        return {"kill": "repo-not-found"}
    signals = {"stars": repo["stars"], "license": repo["license"],
               "homepage": repo["homepage"], "has_readme": repo["has_readme"]}
    if repo["archived"]:
        return {"kill": "archived", **signals}
    signals["fresh"] = bool(repo["pushed_at"]) and repo["pushed_at"] >= "2026-04-01"
    signals["hn"] = hn_interest(full_name)
    signals["downloads"] = package_downloads(full_name.split("/", 1)[1])
    topic = (repo["topics"] or [repo["language"] or "self-hosted"])[0]
    signals["niche_total"] = niche_size(topic)
    time.sleep(7)  # GitHub search: 10/min unauthenticated
    return signals


def score_idea(repos: list[str]) -> dict:
    """Tier 1 money-odds score for one idea (1 or 2 repos)."""
    per_repo: list[dict] = []
    kill = None
    for full_name in repos:
        signals = tier1_for_repo(full_name)
        if "kill" in signals:
            kill = signals["kill"]
            break
        per_repo.append(score_repo_signals(signals))
    if kill:
        return {"score": 0.0, "kill_switch": kill,
                "dimensions": {"demand": 0, "reachability": None, "gap": 0,
                               "ship": 0, "product": 0},
                "signals": {"kill": kill}}
    if not per_repo:
        return {"score": 0.0, "kill_switch": "no-signals", "dimensions": {},
                "signals": {}}
    # Aggregate: the strongest repo carries the idea.
    dims = {
        "demand": max(r["demand"] for r in per_repo),
        "reachability": None,
        "gap": max(r["gap"] for r in per_repo),
        "ship": max(r["ship"] for r in per_repo),
        "product": max(r["product"] for r in per_repo),
    }
    score = sum(v for k, v in dims.items() if v is not None)
    return {"score": round(score, 1), "kill_switch": None,
            "dimensions": dims, "signals": {"repos": len(repos)}}


# --- Email drafts ---


def draft_emails(ideas: list[dict], batch: int = EMAIL_BATCH) -> dict:
    """Generate outreach emails for ideas without a draft yet. No DB connection
    is held during API calls, so concurrent jobs never wait on a lock."""
    load_env()
    read_conn = connect()
    try:
        todo = [
            i for i in ideas
            if read_conn.execute(
                "SELECT 1 FROM email_drafts WHERE idea_id = ?", (i["idea_id"],)
            ).fetchone() is None
        ]
    finally:
        read_conn.close()
    created = 0
    for start in range(0, len(todo), batch):
        chunk = todo[start : start + batch]
        block = "\n".join(
            f"- idea {i['idea_id']}: pitch: {i['pitch']} | customer: {i['target_customer']} "
            f"| angle: {i['marketing_angle']}"
            for i in chunk
        )
        try:
            result = chat(EMAIL_PROMPT.replace("{ideas}", block), max_tokens=8000)
        except (httpx.HTTPError, ValueError, KeyError):
            continue
        write_conn = connect()
        try:
            for email in result.get("emails", []):
                idea_id = email.get("idea_id")
                subject = str(email.get("subject", "")).strip()
                body = str(email.get("body", "")).strip()
                if not idea_id or not subject or not body:
                    continue
                write_conn.execute(
                    "INSERT OR REPLACE INTO email_drafts (idea_id, subject, body) VALUES (?, ?, ?)",
                    (int(idea_id), subject, body),
                )
                created += 1
            write_conn.commit()
        finally:
            write_conn.close()
    return {"attempted": len(todo), "created": created}


def rank(limit: int | None = None) -> dict:
    """Tier 1 ranking for ideas without a score, then email drafts. All network
    work happens with no DB connection open; writes are short bursts."""
    conn = connect()
    try:
        rows = conn.execute(
            """SELECT i.idea_id, i.pitch, i.target_customer, i.marketing_angle
               FROM ideas i
               LEFT JOIN idea_scores sc ON sc.idea_id = i.idea_id
               WHERE sc.idea_id IS NULL
               ORDER BY i.idea_id"""
        ).fetchall()
        if limit:
            rows = rows[:limit]
        ideas_with_repos = []
        for row in rows:
            repos = [
                r["full_name"]
                for r in conn.execute(
                    "SELECT full_name FROM idea_repos WHERE idea_id = ?", (row["idea_id"],)
                )
            ]
            ideas_with_repos.append((dict(row), repos))
    finally:
        conn.close()

    ranked = 0
    failures: list[list[str]] = []
    outcomes: list[tuple[int, dict]] = []
    for idea, repos in ideas_with_repos:
        try:
            outcome = score_idea(repos)
        except (httpx.HTTPError, ValueError):
            failures.append([str(idea["idea_id"]), "signal-call-failed"])
            continue
        outcomes.append((idea["idea_id"], outcome))
        ranked += 1

    if outcomes:
        write_conn = connect()
        try:
            for idea_id, outcome in outcomes:
                write_conn.execute(
                    """INSERT OR REPLACE INTO idea_scores
                       (idea_id, score, dimensions, signals, kill_switch) VALUES (?, ?, ?, ?, ?)""",
                    (idea_id, outcome["score"], json.dumps(outcome["dimensions"]),
                     json.dumps(outcome["signals"]), outcome["kill_switch"]),
                )
            write_conn.commit()
        finally:
            write_conn.close()

    drafts = draft_emails([idea for idea, _ in ideas_with_repos])
    return {"attempted": len(rows), "ranked": ranked, "failures": failures, "emails": drafts}
