"""MCP server for GITBUTT: exposes the repo database and pipelines as tools.

Runs over stdio, launched by ZCode from the plugin manifest. Everything is
driven by natural language in a session; nothing runs automatically. Tools
that hit the network or the model (scrape_new, summarize_missing,
build_ideas, rank_ideas) mutate the database, so call status() first when
in doubt.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from gitbutt.categories import load_taxonomy
from gitbutt.db import connect
from gitbutt.ideas import generate as generate_ideas
from gitbutt.ranking import rank as rank_tier1
from gitbutt.scrape import scrape as run_scrape
from gitbutt.summaries import summarize_missing as run_summarize
from gitbutt.tier2 import tier2 as tier2_rank

mcp = FastMCP("gitbutt")


@mcp.tool()
def status() -> dict:
    """Counts and freshness: videos, repos, summaries, ideas, scores."""
    conn = connect()
    try:
        counts = {
            "videos": conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0],
            "repos": conn.execute("SELECT COUNT(*) FROM repos").fetchone()[0],
            "summarized": conn.execute("SELECT COUNT(*) FROM repo_summaries").fetchone()[0],
            "ideas": conn.execute("SELECT COUNT(*) FROM ideas").fetchone()[0],
            "scored_ideas": conn.execute("SELECT COUNT(*) FROM idea_scores").fetchone()[0],
        }
        counts["missing_summaries"] = counts["repos"] - counts["summarized"]
        counts["last_scrape"] = conn.execute("SELECT MAX(fetched_at) FROM videos").fetchone()[0]
        return counts
    finally:
        conn.close()


@mcp.tool()
def scrape_new() -> dict:
    """Fetch new @GithubAwesome videos from the channel RSS and extract the
    repos they mention. On demand only; mutates the database."""
    return run_scrape()


@mcp.tool()
def summarize_missing(limit: int | None = None) -> dict:
    """Summarize repos that have no summary yet (DeepSeek + README excerpts).
    Mutates the database."""
    return run_summarize(limit=limit)


@mcp.tool()
def search_repos(query: str, limit: int = 10) -> dict:
    """Find repos matching free-text keywords. Searches repo names, tags,
    summaries, and categories."""
    conn = connect()
    try:
        like = f"%{query}%"
        rows = conn.execute(
            """SELECT r.full_name, r.category, s.summary, s.tags
               FROM repos r
               JOIN repo_summaries s ON s.full_name = r.full_name
               WHERE r.full_name LIKE ? OR s.summary LIKE ? OR s.tags LIKE ? OR r.category LIKE ?
               ORDER BY r.full_name
               LIMIT ?""",
            (like, like, like, like, limit),
        ).fetchall()
        return {"query": query, "count": len(rows), "repos": [dict(row) for row in rows]}
    finally:
        conn.close()


@mcp.tool()
def build_ideas(theme: str | None = None, count: int = 10) -> dict:
    """Generate product ideas from the repo pool: one or two repos glued into
    a pitched concept. Optional theme focuses the run; without one, the
    generator picks the strongest across categories."""
    return generate_ideas(max_ideas=min(count, 10), theme=theme)


@mcp.tool()
def landscape(topic: str | None = None) -> dict:
    """Briefing on the repo taxonomy: category definitions, related
    categories, and repo counts. With a topic, only matching categories are
    returned; if none match, falls back to a repo search."""
    categories = load_taxonomy()
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT category, COUNT(*) AS n FROM repos WHERE category IS NOT NULL GROUP BY category"
        ).fetchall()
    finally:
        conn.close()
    counts = {row["category"]: row["n"] for row in rows}
    brief = []
    for cat in categories:
        if topic and topic.lower() not in cat["name"].lower():
            continue
        brief.append(
            {
                "category": cat["name"],
                "definition": cat["definition"],
                "related": cat.get("related", []),
                "repo_count": counts.get(cat["name"], 0),
            }
        )
    if topic and not brief:
        return search_repos(topic, limit=10)
    return {"topic": topic or "all", "categories": brief}


@mcp.tool()
def spotlight(repo: str) -> dict:
    """Deep dive on one repo: summary, tags, category, the video it first
    appeared in, and every idea it is used in."""
    conn = connect()
    try:
        row = conn.execute(
            """SELECT r.full_name, r.owner, r.name, r.category, r.first_seen_video,
                      r.first_seen_at, s.summary, s.tags
               FROM repos r
               LEFT JOIN repo_summaries s ON s.full_name = r.full_name
               WHERE r.full_name = ?""",
            (repo,),
        ).fetchone()
        if row is None:
            return {"found": False, "repo": repo}
        ideas = [
            dict(i)
            for i in conn.execute(
                """SELECT i.idea_id, i.pitch FROM ideas i
                   JOIN idea_repos ir ON ir.idea_id = i.idea_id
                   WHERE ir.full_name = ?
                   ORDER BY i.idea_id""",
                (repo,),
            )
        ]
        video = conn.execute(
            "SELECT title FROM videos WHERE video_id = ?", (row["first_seen_video"],)
        ).fetchone()
        return {
            "found": True,
            "repo": dict(row),
            "first_seen_video_title": video["title"] if video else None,
            "used_in_ideas": ideas,
        }
    finally:
        conn.close()


@mcp.tool()
def digest(limit: int = 10) -> dict:
    """Fresh picks: the most recently added repos, newest first."""
    conn = connect()
    try:
        rows = conn.execute(
            """SELECT r.full_name, r.category, r.first_seen_at, s.summary
               FROM repos r
               JOIN repo_summaries s ON s.full_name = r.full_name
               ORDER BY r.first_seen_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return {"count": len(rows), "repos": [dict(row) for row in rows]}
    finally:
        conn.close()


@mcp.tool()
def top_ideas(limit: int = 20) -> dict:
    """The current idea board: pitches with their repos, scores, and email
    drafts, best scored first."""
    conn = connect()
    try:
        rows = conn.execute(
            """SELECT i.idea_id, i.pitch, i.target_customer, i.marketing_angle,
                      sc.score, sc.kill_switch, e.subject, e.body
               FROM ideas i
               LEFT JOIN idea_scores sc ON sc.idea_id = i.idea_id
               LEFT JOIN email_drafts e ON e.idea_id = i.idea_id
               ORDER BY sc.score DESC, i.idea_id
               LIMIT ?""",
            (limit,),
        ).fetchall()
        out = []
        for row in rows:
            item = dict(row)
            item["repos"] = [
                r["full_name"]
                for r in conn.execute(
                    "SELECT full_name FROM idea_repos WHERE idea_id = ?", (row["idea_id"],)
                )
            ]
            out.append(item)
        return {"count": len(out), "ideas": out}
    finally:
        conn.close()


@mcp.tool()
def rank_ideas(limit: int = 20) -> dict:
    """Score ideas for money potential on demand: Tier 1 signals and outreach
    email drafts, then Tier 2 reachability and pricing for the top ones. Hits
    the network; run it only when a scored shortlist is wanted."""
    tier1 = rank_tier1(limit=limit)
    tier2 = tier2_rank(limit=limit)
    return {"tier1": tier1, "tier2": tier2}


if __name__ == "__main__":
    mcp.run()
