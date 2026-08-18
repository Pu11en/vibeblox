"""Idea generation agent: DeepSeek V4 Flash turns repos into product ideas.

Step 3 (2026-08-02): the generator reads the category landscape instead of a
flat repo list. The digest mirrors the wiki concept pages (data/taxonomy.json
is the same source the wiki is regenerated from): category name, definition,
related categories, and the least-used repos per category.

Locked rules (wayfinder ticket Set the idea generation rules):
- single-repo ideas always allowed; combos of exactly two repos with a stated fit
- up to 10 new ideas per run, dedupe by repo set (a pairing never repeats)
- repos used in 5+ ideas are excluded from the candidate pool
"""

from __future__ import annotations

import re
import sqlite3

import httpx

from gitbutt.categories import load_taxonomy
from gitbutt.db import connect
from gitbutt.deepseek import chat

MAX_IDEAS = 10
MAX_USES = 5
REPOS_PER_CATEGORY = 6
SUMMARY_CHARS = 140

IDEA_PROMPT = """You are a product strategist for indie engineers. Below is the open source repo landscape from a trending GitHub channel, organized by category. Each category has a definition, related categories, and repos with one-line summaries.

Think in category combinations. A tool from one category plus a tool from another often becomes a product for a specific customer. Example: "a self-hosted billing tool plus a link shortener serves freelancers."

Create product ideas with these rules:
- Use ONLY repos from the list, by their exact owner/repo name.
- Each idea uses exactly 1 repo, or exactly 2 repos.
- For 2-repo ideas, the fit must be real and stated in one sentence: "X handles A, Y handles B, together they are a C-for-D product." Name both categories in the fit.
- Open the pitch with the category combination, e.g. "Self-hosted sync + private notes = a health journal you own." This makes the landscape thinking visible.
- Name a clear target customer and the simplest email-marketing angle (who to email, what the pitch is).
- Prefer ideas an engineer could ship in a week by cloning and gluing these repos.
- Vary the categories: do not use the same category in every idea.

Theme: {theme}

Return ONLY JSON, no prose:
{"ideas": [{"pitch": "...", "repos": ["owner/repo"], "target_customer": "...", "marketing_angle": "...", "fit": "..."}]}

Landscape:
{repos}
"""


def _landscape_digest(conn: sqlite3.Connection) -> tuple[set[str], str]:
    """Build the category digest: taxonomy (names, definitions, related) plus
    the least-used repos per category. Returns (allowed repo names, prompt block).

    Mirrors the wiki/concepts pages, which are generated from the same
    taxonomy and repo data. The wiki pages themselves carry no use counts,
    so the digest is built from the DB to keep the locked rule: repos used
    in 5+ ideas are excluded, lowest-use repos shown first.
    """
    categories = load_taxonomy()
    names = {c["name"] for c in categories}
    rows = conn.execute(
        """SELECT r.full_name, r.category, s.summary,
                  (SELECT COUNT(*) FROM idea_repos ir WHERE ir.full_name = r.full_name) AS uses
           FROM repos r
           JOIN repo_summaries s ON s.full_name = r.full_name
           WHERE r.category IS NOT NULL
             AND (SELECT COUNT(*) FROM idea_repos ir WHERE ir.full_name = r.full_name) < ?
           ORDER BY uses ASC, r.full_name""",
        (MAX_USES,),
    ).fetchall()
    by_category: dict[str, list[dict]] = {}
    for row in rows:
        by_category.setdefault(row["category"], []).append(dict(row))

    lines: list[str] = []
    pool: set[str] = set()
    for category in categories:
        name = category["name"]
        repos = by_category.get(name, [])[:REPOS_PER_CATEGORY]
        if not repos:
            continue
        related = [r for r in category.get("related", []) if r in names and r != name][:3]
        rel = ", ".join(related) if related else "none"
        lines.append(f"## {name}: {category['definition']} (related: {rel})")
        for repo in repos:
            summary = re.sub(r"\s+", " ", repo["summary"]).strip()[:SUMMARY_CHARS]
            lines.append(f"- {repo['full_name']}: {summary}")
            pool.add(repo["full_name"])
        lines.append("")
    return pool, "\n".join(lines)


def _pairing_exists(conn: sqlite3.Connection, repos: list[str]) -> bool:
    if len(repos) == 1:
        return (
            conn.execute(
                """SELECT 1 FROM idea_repos
                   WHERE full_name = ? AND idea_id IN
                     (SELECT idea_id FROM idea_repos GROUP BY idea_id HAVING COUNT(*) = 1)""",
                (repos[0],),
            ).fetchone()
            is not None
        )
    return (
        conn.execute(
            """SELECT 1 FROM idea_repos a JOIN idea_repos b ON a.idea_id = b.idea_id
               WHERE a.full_name = ? AND b.full_name = ? AND a.full_name < b.full_name
                 AND (SELECT COUNT(*) FROM idea_repos WHERE idea_id = a.idea_id) = 2""",
            (min(repos), max(repos)),
        ).fetchone()
        is not None
    )


def generate(max_ideas: int = MAX_IDEAS, theme: str | None = None) -> dict:
    conn = connect()
    try:
        pool, block = _landscape_digest(conn)
        if not pool:
            return {"candidates_seen": 0, "requested": 0, "created": 0, "skipped": [], "reason": "no categorized candidates"}
        prompt = IDEA_PROMPT.replace("{theme}", theme or "none, pick the strongest ideas across categories")
        try:
            result = chat(prompt.replace("{repos}", block), max_tokens=8000)
        except (httpx.HTTPError, ValueError, KeyError):
            return {
                "candidates_seen": len(pool),
                "requested": 0,
                "created": 0,
                "skipped": [["api-error", "idea generation call failed"]],
            }
        created = 0
        skipped: list[list[str]] = []
        for idea in result.get("ideas", []):
            if created >= max_ideas:
                break
            repos = [r for r in (idea.get("repos") or []) if isinstance(r, str) and r in pool]
            repos = list(dict.fromkeys(repos))
            if len(repos) not in (1, 2):
                skipped.append(["bad-repo-count", str(idea.get("pitch", ""))[:60]])
                continue
            if _pairing_exists(conn, repos):
                skipped.append(["duplicate-pairing", "/".join(repos)])
                continue
            cur = conn.execute(
                """INSERT INTO ideas (pitch, target_customer, marketing_angle, source_run)
                   VALUES (?, ?, ?, ?)""",
                (
                    str(idea.get("pitch", "")).strip(),
                    str(idea.get("target_customer", "")).strip(),
                    str(idea.get("marketing_angle", "")).strip(),
                    "generate",
                ),
            )
            idea_id = cur.lastrowid
            for full_name in repos:
                conn.execute(
                    "INSERT INTO idea_repos (idea_id, full_name) VALUES (?, ?)", (idea_id, full_name)
                )
            created += 1
        conn.commit()
        return {
            "candidates_seen": len(pool),
            "requested": len(result.get("ideas", [])),
            "created": created,
            "skipped": skipped,
        }
    finally:
        conn.close()
