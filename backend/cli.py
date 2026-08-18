#!/usr/bin/env python3
"""Play2Build CLI — the game's loop inside the harness.

Pick an idea, answer A/B/C questions, watch the workers, get a real repo.
Same backend, same brain, same pipeline as the Roblox game — just terminal.

Usage:
  python3 cli.py                # interactive
  python3 cli.py --auto snake-game a a a   # non-interactive (for tests/agents)
"""
import argparse
import json
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8000"
SECRET = None  # loaded from backend/.env


def load_env():
    import os
    from pathlib import Path
    env = Path(__file__).resolve().parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
    global SECRET
    SECRET = os.environ.get("P2B_SECRET", "dev-secret-change-me")


def get(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("X-P2B-Secret", SECRET)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(), method="POST")
    req.add_header("X-P2B-Secret", SECRET)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def ask(prompt, options):
    """Print options as A/B/C/D, read a line, return the option index.
    'build' / 'done' / 'enough' / 'stop' ends the questions early (None)."""
    keys = "abcd"[:len(options)]
    print("\n" + prompt)
    for key, label, desc in options:
        print(f"  {key.upper()}. {label} — {desc}")
    while True:
        answer = input("> ").strip().lower()
        if answer in ("build", "done", "enough", "stop"):
            return None
        if answer in keys:
            return keys.index(answer)
        print(f"  (type one of: {', '.join(k.upper() for k in keys)}, or 'build' to stop)")


def pick_idea(ideas):
    print("\n" + "=" * 50)
    print("PLAY2BUILD — pick an idea. The workers build it for real.")
    print("=" * 50)
    for i, idea in enumerate(ideas, 1):
        print(f"  [{i:>2}] {idea['name']} — {idea['description']}")
    print(f"  [{len(ideas) + 1:>2}] Surprise me")
    print(f"  [ {0} ] Type your own idea")
    while True:
        raw = input("> ").strip()
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(ideas):
                return ideas[n - 1]
            if n == len(ideas) + 1:
                import random
                return random.choice(ideas)
            if n == 0:
                name = input("What do you want to build? ").strip()
                if name:
                    return {"id": "custom", "name": name,
                            "description": f"A {name}, built from scratch by the workers."}
        print(f"  (type a number 1-{len(ideas) + 1}, 0 to type your own)")


def run(auto_idea=None, auto_answers=None, auto_name=None, find_idea=False):
    ideas = get("/api/ideas")["ideas"]
    questions = get("/api/questions")["questions"]

    if find_idea:
        import idea_finder
        card = idea_finder.find("fresh", 5)
        if not card:
            return 1
        idea = {"id": "custom", "emoji": "", "name": card.get("name", "Idea"),
                "description": card.get("pitch", "")}
        print(f"\nIdea Finder picked: {idea['name']}")
    elif auto_idea:
        if auto_idea == "custom":
            name = auto_name or "Custom Project"
            idea = {"id": "custom", "emoji": "", "name": name,
                    "description": f"A {name}, built from scratch by the workers."}
        else:
            idea = next((i for i in ideas if i["id"] == auto_idea), ideas[0])
    else:
        idea = pick_idea(ideas)

    # brain-proposed questions for this idea (static set as fallback)
    try:
        req = urllib.request.Request(
            BASE + "/api/questions/for-idea",
            data=json.dumps({"idea": idea}).encode(), method="POST")
        req.add_header("X-P2B-Secret", SECRET)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=30) as r:
            qdata = json.loads(r.read()).get("questions")
        if isinstance(qdata, list) and qdata:
            questions = qdata
    except Exception:
        pass  # static questions

    answers = []
    if auto_answers:
        for i, q in enumerate(questions):
            key = auto_answers[i] if i < len(auto_answers) else "a"
            idx = "abcd".index(key)
            opt = q["options"][min(idx, len(q["options"]) - 1)]
            answers.append({"id": q["id"], "text": q["text"], "label": opt["label"]})
            print(f"\n{q['text']}\n  -> {key.upper()}. {opt['label']}")
    else:
        for i, q in enumerate(questions, 1):
            opts = [("abcd"[j], o["label"], o["description"]) for j, o in enumerate(q["options"])]
            idx = ask(f"Question {i} of {len(questions)}: {q['text']}", opts)
            if idx is None:
                print("  (enough answers - building now)")
                break
            opt = q["options"][idx]
            answers.append({"id": q["id"], "text": q["text"], "label": opt["label"]})

    print(f"\nStarting: {idea['name']}")
    import board
    board_key = board.add_idea(idea)
    job = post("/api/start", {"idea": idea, "answers": answers, "playerName": "cli"})
    job_id = job["jobId"]

    last_stage = None
    t0 = time.time()
    while True:
        time.sleep(3)
        snap = get(f"/api/status?job={job_id}")
        stage, message = snap["stage"], snap["message"]
        if stage != last_stage:
            print(f"  [{int(time.time() - t0):>3}s] {message}")
            if snap.get("detail") and stage in ("planning", "writing"):
                print(f"         plan: {snap['detail'][:160]}")
            last_stage = stage
        if snap["state"] == "done":
            print("\n" + "=" * 50)
            print(f"Done. Repo: {snap['repoUrl']}")
            if snap.get("runCommand"):
                print(f"Run: {snap['runCommand']}")
            print(f"   cost: ${snap['costUsd']:.4f} | took {snap['elapsedMs'] / 1000:.0f}s")
            print("=" * 50)
            import board
            board.add_block(board_key, {
                "name": idea["name"], "status": "done",
                "repoUrl": snap.get("repoUrl"), "cost": snap.get("costUsd", 0),
                "seconds": int((snap.get("elapsedMs") or 0) / 1000),
                "answers": len(answers),
            })
            return 0
        if snap["state"] == "failed":
            print(f"\nBuild failed: {snap.get('detail') or snap.get('message')}")
            import board
            board.add_block(board_key, {
                "name": idea["name"], "status": "failed",
                "cost": snap.get("costUsd", 0),
                "seconds": int((snap.get("elapsedMs") or 0) / 1000),
                "answers": len(answers),
            })
            return 1


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-idea", help="idea id for non-interactive runs ('custom' + --auto-name for any idea)")
    ap.add_argument("--auto-name", help="name for --auto-idea custom")
    ap.add_argument("--auto-answers", nargs="+", help="a/b/c answers (one per question)")
    ap.add_argument("--find-idea", action="store_true", help="run the Idea Finder first, then build its pick")
    ap.add_argument("--board", action="store_true", help="show the board (ideas + builds)")
    args = ap.parse_args()
    try:
        if args.board:
            import board
            print(board.show())
            return 0
        return run(args.auto_idea, args.auto_answers, args.auto_name, args.find_idea)
    except urllib.error.URLError as e:
        print(f"\n❌ Can't reach the factory at {BASE} — is backend/run.sh running? ({e})")
        return 1
    except KeyboardInterrupt:
        print("\nbye!")
        return 130


if __name__ == "__main__":
    sys.exit(main())
