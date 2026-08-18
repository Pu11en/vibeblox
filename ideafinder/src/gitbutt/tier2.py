"""Tier 2 ranking: email reachability (25 pts) plus pricing evidence for the top ideas.

Implements the approved rubric (wayfinder ticket Name the money-odds rubric).
Tier 1 (ranking.py) covers demand, ship ease, product potential, and niche
size. Tier 2 adds the two missing dimensions for the top-20 shortlist:

- Email reachability (25 pts), two halves:
  - Community volume (12.5): pullpush.io subreddit search hits for the
    niche keyword. The archive is frozen May 2025, so this is a historical
    floor, and the API caps at 100 hits, which matches the rubric bar:
    "Can we find 100+ people with this problem who read email?"
  - Newsletter coverage (12.5): HN Algolia "substack.com {kw}" hit count,
    the verified way to find Substack newsletters covering a niche.
- Pricing evidence (gap bonus): the repo homepage HTML is fetched and
  scanned for dollar amounts. A price point on the page proves the niche
  has paying customers, which lifts the competitive-gap dimension.

Every point is backed by a stored evidence excerpt in idea_scores.signals.
Runs only for ideas that have a Tier 1 score but no Tier 2 evidence yet,
so reruns are idempotent and cheap.
"""

from __future__ import annotations

import json
import math
import re
import sqlite3
import time

import httpx

from gitbutt.db import connect
from gitbutt.ranking import W_GAP, gh_repo

UA = {"User-Agent": "gitbutt/0.1"}
COMMUNITY_CAP = 100  # pullpush returns at most 100 hits per query
NEWSLETTER_CAP = 2.0  # 100 newsletters on the keyword = full half
KEYWORDS_PER_IDEA = 3
PRICING_BONUS = 4.0  # price point found on the repo homepage
PRICE_RE = re.compile(r"\$\s?\d{1,3}(?:[.,]\d{2,3})?(?:\s?(?:/|per)\s?(?:mo|month|user|seat|year))?", re.IGNORECASE)


def _get(url: str, timeout: float = 30.0) -> httpx.Response:
    resp = httpx.get(url, headers=UA, timeout=timeout, follow_redirects=True)
    resp.raise_for_status()
    return resp


# --- Keyword derivation (deterministic, no LLM) ---


def keywords_for_idea(conn: sqlite3.Connection, idea_id: int) -> list[str]:
    """Niche keywords for one idea: top tags of its repos, deduped.

    Falls back to the repo categories, then to the repo names.
    """
    repos = [
        r["full_name"]
        for r in conn.execute("SELECT full_name FROM idea_repos WHERE idea_id = ?", (idea_id,))
    ]
    keywords: list[str] = []
    seen: set[str] = set()
    for full_name in repos:
        row = conn.execute(
            "SELECT tags FROM repo_summaries WHERE full_name = ?", (full_name,)
        ).fetchone()
        if row:
            try:
                tags = [str(t).strip() for t in json.loads(row["tags"] or "[]")]
            except (json.JSONDecodeError, TypeError):
                tags = []
            for tag in tags:
                kw = tag.lower()
                if kw not in seen:
                    seen.add(kw)
                    keywords.append(kw)
    if len(keywords) < KEYWORDS_PER_IDEA:
        for full_name in repos:
            row = conn.execute("SELECT category FROM repos WHERE full_name = ?", (full_name,)).fetchone()
            if row and row["category"]:
                kw = str(row["category"]).lower()
                if kw not in seen:
                    seen.add(kw)
                    keywords.append(kw)
    if not keywords:
        keywords = [full_name.split("/", 1)[1].lower() for full_name in repos]
    return keywords[:KEYWORDS_PER_IDEA]


# --- Tier 2 signals ---


def community_volume(keyword: str) -> dict:
    """S8: subreddit posts mentioning the keyword, via pullpush.io."""
    try:
        data = _get(
            f"https://api.pullpush.io/reddit/search/submission/?q={keyword}&size={COMMUNITY_CAP}"
        ).json()
        hits = len(data.get("data") or [])
        return {"hits": hits, "cap": COMMUNITY_CAP}
    except httpx.HTTPError:
        return {"hits": 0, "cap": COMMUNITY_CAP}


def newsletter_coverage(keyword: str) -> dict:
    """S9: Substack newsletters covering the keyword, via HN Algolia."""
    try:
        data = _get(
            f"https://hn.algolia.com/api/v1/search?query=substack.com%20{keyword}&tags=story&hitsPerPage=3"
        ).json()
        return {"nbHits": int(data.get("nbHits") or 0)}
    except httpx.HTTPError:
        return {"nbHits": 0}


def pricing_evidence(full_name: str) -> dict | None:
    """S10: dollar amounts on the repo homepage. None when no homepage or
    the page is unreachable or has no price, so the gap keeps its Tier 1 value."""
    repo = gh_repo(full_name)
    if repo is None or not repo.get("homepage"):
        return None
    try:
        resp = _get(repo["homepage"], timeout=20.0)
        text = resp.text[:200_000]
    except httpx.HTTPError:
        return None
    match = PRICE_RE.search(text)
    if not match:
        return None
    start = max(0, match.start() - 60)
    end = min(len(text), match.end() + 60)
    excerpt = re.sub(r"\s+", " ", text[start:end]).strip()
    return {"url": repo["homepage"], "price": match.group(0), "excerpt": excerpt[:180]}


# --- Scoring ---


def score_reachability(community: dict, newsletters: dict) -> float:
    community_pts = min(1.0, community["hits"] / COMMUNITY_CAP) * 12.5
    newsletter_pts = min(1.0, math.log10(1 + newsletters["nbHits"]) / NEWSLETTER_CAP) * 12.5
    return round(community_pts + newsletter_pts, 1)


def tier2_for_idea(conn: sqlite3.Connection, idea_id: int) -> dict:
    """Full Tier 2 pass for one idea. Returns the updated dimensions and
    the evidence to store in idea_scores.signals."""
    keywords = keywords_for_idea(conn, idea_id)
    community_best = {"hits": 0, "cap": COMMUNITY_CAP}
    newsletter_best = {"nbHits": 0}
    keyword_evidence: list[dict] = []
    for kw in keywords:
        community = community_volume(kw)
        newsletters = newsletter_coverage(kw)
        keyword_evidence.append(
            {"keyword": kw, "community": community["hits"], "newsletters": newsletters["nbHits"]}
        )
        if community["hits"] > community_best["hits"]:
            community_best = community
        if newsletters["nbHits"] > newsletter_best["nbHits"]:
            newsletter_best = newsletters
        time.sleep(1)  # be polite to pullpush and HN

    repos = [
        r["full_name"]
        for r in conn.execute("SELECT full_name FROM idea_repos WHERE idea_id = ?", (idea_id,))
    ]
    pricing = pricing_evidence(repos[0]) if repos else None

    reachability = score_reachability(community_best, newsletter_best)
    evidence = {
        "tier2": {
            "keywords": keyword_evidence,
            "community": community_best,
            "newsletters": newsletter_best,
            "pricing": pricing,
        }
    }
    return {"reachability": reachability, "pricing_bonus": PRICING_BONUS if pricing else 0.0,
            "evidence": evidence}


def apply_tier2(idea_id: int, outcome: dict) -> None:
    """Update the idea_scores row: fill reachability, add the pricing bonus
    to the gap dimension (capped at W_GAP), recompute the total score."""
    conn = connect()
    try:
        row = conn.execute(
            "SELECT dimensions, signals FROM idea_scores WHERE idea_id = ?", (idea_id,)
        ).fetchone()
        if row is None:
            return
        dims = json.loads(row["dimensions"] or "{}")
        signals = json.loads(row["signals"] or "{}")
        dims["reachability"] = outcome["reachability"]
        if outcome["pricing_bonus"] and isinstance(dims.get("gap"), (int, float)):
            dims["gap"] = round(min(W_GAP, dims["gap"] + outcome["pricing_bonus"]), 1)
        signals.update(outcome["evidence"])
        total = round(sum(v for v in dims.values() if isinstance(v, (int, float))), 1)
        conn.execute(
            """UPDATE idea_scores
               SET score = ?, dimensions = ?, signals = ?,
                   scored_at = datetime('now')
               WHERE idea_id = ?""",
            (total, json.dumps(dims), json.dumps(signals), idea_id),
        )
        conn.commit()
    finally:
        conn.close()


def tier2(limit: int = 20) -> dict:
    """Tier 2 for the top ideas that have a Tier 1 score but no Tier 2
    evidence yet. Idempotent: reruns skip ideas that already have it."""
    conn = connect()
    try:
        rows = conn.execute(
            """SELECT i.idea_id
               FROM ideas i
               JOIN idea_scores sc ON sc.idea_id = i.idea_id
               WHERE sc.signals IS NULL OR sc.signals NOT LIKE '%"tier2"%'
               ORDER BY sc.score DESC, i.idea_id
               LIMIT ?""",
            (limit,),
        ).fetchall()
        todo = [r["idea_id"] for r in rows]
    finally:
        conn.close()

    scored = 0
    failures: list[list[str]] = []
    for idea_id in todo:
        try:
            read_conn = connect()
            try:
                outcome = tier2_for_idea(read_conn, idea_id)
            finally:
                read_conn.close()
        except (httpx.HTTPError, ValueError):
            failures.append([str(idea_id), "tier2-signal-failed"])
            continue
        apply_tier2(idea_id, outcome)
        scored += 1
    return {"attempted": len(todo), "scored": scored, "failures": failures}
