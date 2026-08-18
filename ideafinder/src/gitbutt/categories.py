"""Repo category wiki: taxonomy, classification, and LLM Wiki page generation.

One repeatable command: `uv run gitbutt wiki`. It proposes a taxonomy
from a sample of repos (stored in data/taxonomy.json), classifies every repo
without a category (stored in repos.category), and regenerates the wiki pages
under wiki/concepts/. The database is the source of truth; pages are views.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import httpx

from gitbutt.db import PROJECT_ROOT, connect
from gitbutt.deepseek import chat, load_env

WIKI_DIR = PROJECT_ROOT / "wiki"
CONCEPTS_DIR = WIKI_DIR / "concepts"
TAXONOMY_PATH = PROJECT_ROOT / "data" / "taxonomy.json"
TOP_CATEGORIES = 18
MIN_TAG_COUNT = 8

DEFINITIONS_PROMPT = """Define each of these repo categories in under 15 words each.

Categories: {names}

Return ONLY JSON: {{"category name": "short definition"}}
"""


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "uncategorized"


def _definitions(names: list[str]) -> dict[str, str]:
    """One small LLM call for definitions. Tolerant: falls back to the bare name."""
    load_env()
    try:
        result = chat(
            DEFINITIONS_PROMPT.replace("{names}", ", ".join(names)), max_tokens=4000
        )
        return {key: str(value) for key, value in result.items() if isinstance(value, str)}
    except (httpx.HTTPError, ValueError, KeyError):
        return {}


def build_taxonomy_from_tags() -> list[dict]:
    """Derive the taxonomy from the repo tag data: top tags are the categories,
    co-occurrence on the same repos defines the related links. Deterministic,
    no open-ended model call to overthink."""
    from collections import Counter, defaultdict

    conn = connect()
    try:
        rows = conn.execute("SELECT tags FROM repo_summaries").fetchall()
    finally:
        conn.close()
    counter: Counter[str] = Counter()
    per_repo: list[set[str]] = []
    for row in rows:
        try:
            tags = {str(t).strip().lower() for t in json.loads(row["tags"] or "[]")}
        except (json.JSONDecodeError, TypeError):
            tags = set()
        per_repo.append(tags)
        counter.update(tags)
    top = [name for name, count in counter.most_common(TOP_CATEGORIES) if count >= MIN_TAG_COUNT]
    if len(top) < 6:
        top = [name for name, _ in counter.most_common(TOP_CATEGORIES)]
    top_set = set(top)
    cooccur: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for tags in per_repo:
        for a in tags:
            if a in top_set:
                for b in tags:
                    if b in top_set and b != a:
                        cooccur[a][b] += 1
    definitions = _definitions(top)
    categories = [
        {
            "name": name,
            "definition": definitions.get(name, name),
            "related": [other for other, _ in cooccur[name].most_common(4)],
        }
        for name in top
    ]
    TAXONOMY_PATH.parent.mkdir(parents=True, exist_ok=True)
    TAXONOMY_PATH.write_text(json.dumps(categories, indent=2), encoding="utf-8")
    return categories


def load_taxonomy() -> list[dict]:
    if not TAXONOMY_PATH.exists():
        return build_taxonomy_from_tags()
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


def classify_missing() -> dict:
    """Assign categories deterministically: a repo's category is its first tag
    that exists in the taxonomy. No API calls, instant, reproducible."""
    categories = load_taxonomy()
    top_tags = {c["name"].lower(): c["name"] for c in categories}
    conn = connect()
    try:
        rows = conn.execute(
            """SELECT r.full_name, COALESCE(s.tags, '[]') AS tags
               FROM repos r
               LEFT JOIN repo_summaries s ON s.full_name = r.full_name
               WHERE r.category IS NULL
               ORDER BY r.full_name"""
        ).fetchall()
        classified = 0
        unclassified = 0
        for row in rows:
            try:
                tags = [str(t).strip().lower() for t in json.loads(row["tags"] or "[]")]
            except (json.JSONDecodeError, TypeError):
                tags = []
            category = next((top_tags[t] for t in tags if t in top_tags), None)
            if category:
                conn.execute(
                    "UPDATE repos SET category = ? WHERE full_name = ?",
                    (category, row["full_name"]),
                )
                classified += 1
            else:
                unclassified += 1
        conn.commit()
        return {"attempted": len(rows), "classified": classified, "unclassified": unclassified}
    finally:
        conn.close()


def build_wiki() -> dict:
    """Regenerate wiki/concepts pages, index.md, and log.md from the database."""
    categories = load_taxonomy()
    CONCEPTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    conn = connect()
    try:
        repo_rows = conn.execute(
            """SELECT r.full_name, r.category, COALESCE(s.summary, '') AS summary
               FROM repos r
               LEFT JOIN repo_summaries s ON s.full_name = r.full_name
               WHERE r.category IS NOT NULL
               ORDER BY r.full_name"""
        ).fetchall()
    finally:
        conn.close()
    by_category: dict[str, list[dict]] = {}
    for row in repo_rows:
        by_category.setdefault(row["category"], []).append(dict(row))

    existing = {c["name"] for c in categories}
    pages_written = 0
    index_entries: list[str] = []
    for category in categories:
        repos = by_category.get(category["name"], [])
        if not repos:
            continue
        slug = _slugify(category["name"])
        related = [c for c in category.get("related", []) if c in existing and c != category["name"]][:4]
        related_links = " ".join(f"[[{_slugify(c)}]]" for c in related)
        lines = [
            "---",
            f"title: {category['name']}",
            f"created: {today}",
            f"updated: {today}",
            "type: concept",
            f"tags: [{category['name']}]",
            "sources: [generated from data/repos.sqlite3]",
            "---",
            "",
            f"# {category['name']}",
            "",
            category["definition"],
            "",
            f"**{len(repos)} repos**",
            "",
        ]
        for repo in repos:
            summary = re.sub(r"\s+", " ", repo["summary"]).strip()
            lines.append(f"- **{repo['full_name']}** - {summary[:160]}")
        lines += ["", "## Related", ""]
        lines.append(related_links if related_links else "None.")
        (CONCEPTS_DIR / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")
        pages_written += 1
        index_entries.append(f"- [[{slug}]] - {category['definition'][:80]}")

    index_entries.sort()
    index = (
        "# Wiki Index\n\n"
        "> Content catalog. Every wiki page listed under its type with a one-line summary.\n"
        "> Read this first to find relevant pages for any query.\n"
        f"> Last updated: {today} | Total pages: {pages_written}\n\n"
        "## Concepts\n"
        + "\n".join(index_entries)
        + "\n"
    )
    (WIKI_DIR / "index.md").write_text(index, encoding="utf-8")

    log_entry = (
        f"## [{today}] update | wiki regenerated\n"
        f"- {pages_written} category pages, {len(repo_rows)} repos classified\n"
    )
    with (WIKI_DIR / "log.md").open("a", encoding="utf-8") as log:
        log.write(log_entry)

    return {"pages": pages_written, "classified_repos": len(repo_rows)}


def wiki() -> dict:
    """Full step 2: taxonomy, classification, wiki pages."""
    categories = load_taxonomy()
    classified = classify_missing()
    built = build_wiki()
    return {"taxonomy_categories": len(categories), "classified": classified, "wiki": built}
