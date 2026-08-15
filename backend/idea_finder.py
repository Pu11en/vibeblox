#!/usr/bin/env python3
"""Idea Finder — on-demand idea cards from the GITBUTT repo pool.

Pulls candidate repos (or gitbutt's ranked ideas) from the pool, scores each
for money potential + fastest go-to-market with DeepSeek, and prints the best
card. Nothing runs automatically — every run is on demand.

Usage:
  python3 idea_finder.py                # score the freshest repos
  python3 idea_finder.py --kind top     # reuse gitbutt's ranked ideas
  python3 idea_finder.py --limit 6      # score more candidates

The winning card is a starting point: humans articulate plans better from
something real than from nothing. Feed the card into cli.py to build it.
"""
import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

import llm

GITBUTT_DB = Path(os.environ.get(
    "GITBUTT_DB", "/home/drewp/main-projects/GITBUTT/data/repos.sqlite3"))


def load_env():
    env = Path(__file__).resolve().parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def pool(kind, limit):
    """Read-only candidate pool from the gitbutt database."""
    db = sqlite3.connect(f"file:{GITBUTT_DB}?mode=ro", uri=True)
    if kind == "top":
        rows = db.execute("""
            SELECT i.pitch, i.target_customer, i.marketing_angle,
                   COALESCE(s.score, 'n/a'), GROUP_CONCAT(r.full_name, '; ')
            FROM ideas i
            LEFT JOIN idea_scores s ON s.idea_id = i.idea_id
            LEFT JOIN idea_repos ir ON ir.idea_id = i.idea_id
            LEFT JOIN repos r ON r.full_name = ir.full_name
            GROUP BY i.idea_id
            ORDER BY COALESCE(s.score, 0) DESC
            LIMIT ?
        """, (limit,))
        return [{"name": r[0][:60], "pitch": r[0], "customer": r[1],
                 "angle": r[2], "score": r[3], "repos": r[4]}
                for r in rows]
    rows = db.execute("""
        SELECT r.full_name, COALESCE(rs.summary, ''), COALESCE(rs.tags, ''), r.category
        FROM repos r
        LEFT JOIN repo_summaries rs ON rs.full_name = r.full_name
        WHERE rs.summary IS NOT NULL
        ORDER BY r.first_seen_at DESC
        LIMIT ?
    """, (limit,))
    return [{"name": r[0], "pitch": r[1][:300], "tags": r[2], "category": r[3]}
            for r in rows]


SCORE_SYSTEM = """You are the Idea Finder for a build machine. Given a repo or
idea, score how likely it is to make real money fast, and the fastest path to
go to market. Think: can this become a product people pay for quickly? What is
the shortest realistic route (content, product, tool, service)? Reply with
ONLY a JSON object:
{"name": string, "pitch": string (one plain sentence),
 "why_money": string (why it can make money, one or two sentences),
 "fastest_path": string (the fastest go-to-market route, one sentence),
 "content_angle": string (one sentence: the angle for a video/social post),
 "score": number (0-10)}
No kid-friendly fluff. Real business judgment."""


def score(candidate):
    user = f"Candidate: {candidate.get('name')}\n{candidate.get('pitch', '')}"
    if candidate.get("tags"):
        user += f"\nTags: {candidate['tags']}"
    if candidate.get("repos"):
        user += f"\nRepos: {candidate['repos']}"
    card, cost = llm.json_call(SCORE_SYSTEM, user, max_tokens=600)
    card["cost"] = cost
    card["starting_point"] = candidate.get("repos") or candidate.get("name")
    return card


def find(kind="fresh", limit=5):
    candidates = pool(kind, limit)
    if not candidates:
        print("Idea Finder: pool is empty — run gitbutt scrape first.")
        return None
    best = None
    for c in candidates:
        try:
            card = score(c)
            print(f"  scored {card.get('name', c['name'])[:50]} -> {card.get('score', '?')}/10")
            if best is None or card.get("score", 0) > best.get("score", 0):
                best = card
        except Exception as e:
            print(f"  scoring failed for {c['name']}: {e}")
    return best


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["fresh", "top"], default="fresh")
    ap.add_argument("--limit", type=int, default=5)
    args = ap.parse_args()
    card = find(args.kind, args.limit)
    if not card:
        return 1
    print("\n" + "=" * 52)
    print(f"💡 IDEA CARD — {card.get('name')}  (score {card.get('score')}/10, ~${card.get('cost', 0):.4f})")
    print(f"   pitch:      {card.get('pitch')}")
    print(f"   why money:  {card.get('why_money')}")
    print(f"   fastest:    {card.get('fastest_path')}")
    print(f"   content:    {card.get('content_angle')}")
    if card.get("starting_point"):
        print(f"   start from: {card.get('starting_point')}")
    print("=" * 52)
    print("Build it: python3 cli.py --find-idea --auto-answers a a b")
    return 0


if __name__ == "__main__":
    sys.exit(main())
