#!/usr/bin/env python3
"""The board — persistent view of ideas and their build blocks.

Everything the player works on lands here: ideas, their builds, statuses,
repos, costs. Plain text, no decoration. State lives in backend/board.json
(gitignored - it is session/user state).
"""
import json
import time
from pathlib import Path

BOARD_FILE = Path(__file__).resolve().parent / "board.json"


def load():
    if BOARD_FILE.exists():
        try:
            return json.loads(BOARD_FILE.read_text())
        except Exception:
            pass
    return {"ideas": []}


def save(board):
    BOARD_FILE.write_text(json.dumps(board, indent=1))


def idea_key(idea):
    name = (idea.get("name") or "idea").strip().lower().replace(" ", "-")[:40]
    return f"{idea.get('id', 'custom')}-{name}"


def add_idea(idea):
    board = load()
    key = idea_key(idea)
    if not any(i["key"] == key for i in board["ideas"]):
        board["ideas"].append({
            "key": key,
            "name": idea.get("name", "Idea"),
            "created": time.strftime("%Y-%m-%d %H:%M"),
            "blocks": [],
        })
        save(board)
    return key


def add_block(idea_key_, block):
    board = load()
    for idea in board["ideas"]:
        if idea["key"] == idea_key_:
            idea["blocks"].append(block)
            save(board)
            return
    # idea missing (state file reset) - recreate it
    board["ideas"].append({"key": idea_key_, "name": block.get("name", "Idea"),
                           "created": time.strftime("%Y-%m-%d %H:%M"), "blocks": [block]})
    save(board)


def show():
    board = load()
    lines = []
    if not board["ideas"]:
        return "Board is empty. Find an idea or build something to start."
    for idea in board["ideas"]:
        lines.append(f"\nIDEA: {idea['name']}  (started {idea['created']})")
        if not idea["blocks"]:
            lines.append("  - no builds yet")
        for b in idea["blocks"]:
            status = b.get("status", "?")
            repo = b.get("repoUrl") or ""
            cost = b.get("cost", 0)
            secs = b.get("seconds", 0)
            q = b.get("answers", 0)
            lines.append(f"  BLOCK: {b.get('name', '?')} [{status}]"
                         + (f" | {repo}" if repo else "")
                         + f" | {cost:.4f}$ | {secs}s | {q} questions")
    return "\n".join(lines)
