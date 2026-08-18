"""Command line entry points for GITBUTT jobs.

Usage:
    uv run gitbutt summarize [N]
    uv run gitbutt scrape
    uv run gitbutt generate [N]
    uv run gitbutt rank [N]
"""

from __future__ import annotations

import sys

from gitbutt.categories import wiki as build_wiki
from gitbutt.db import init_idea_schema
from gitbutt.ideas import generate
from gitbutt.ranking import rank
from gitbutt.scrape import scrape
from gitbutt.summaries import summarize_missing
from gitbutt.tier2 import tier2 as tier2_rank


def cmd_summarize(args: list[str]) -> int:
    limit = int(args[0]) if args and args[0].isdigit() else None
    print(summarize_missing(limit=limit))
    return 0


def cmd_generate(args: list[str]) -> int:
    max_ideas = int(args[0]) if args and args[0].isdigit() else 10
    print(generate(max_ideas=max_ideas))
    return 0


def cmd_rank(args: list[str]) -> int:
    limit = int(args[0]) if args and args[0].isdigit() else None
    print(rank(limit=limit))
    return 0


def cmd_tier2(args: list[str]) -> int:
    limit = int(args[0]) if args and args[0].isdigit() else 20
    print(tier2_rank(limit=limit))
    return 0


def cmd_scrape() -> int:
    print(scrape())
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    init_idea_schema()
    command, rest = args[0], args[1:]
    if command == "summarize":
        return cmd_summarize(rest)
    if command == "generate":
        return cmd_generate(rest)
    if command == "rank":
        return cmd_rank(rest)
    if command == "tier2":
        return cmd_tier2(rest)
    if command == "scrape":
        return cmd_scrape()
    if command == "wiki":
        print(build_wiki())
        return 0
    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
