"""The factory floor: turns an idea + answers into a real public GitHub repo.

Pipeline per job: planning (brain) -> writing files -> checking it runs
-> git init/commit -> create GitHub repo -> push. Progress is written back
to the job dict, which the HTTP server serves to the game.
"""
import json
import os
import re
import shutil
import subprocess
import threading
import time
import traceback
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import llm

ROOT = Path(__file__).resolve().parent
JOBS_DIR = ROOT / "jobs"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_PUBLIC = os.environ.get("GITHUB_PUBLIC", "1") == "1"
REPO_PREFIX = os.environ.get("REPO_PREFIX", "play2build")
ENGINE = os.environ.get("ENGINE", "deepseek")
MAX_WORKERS = int(os.environ.get("P2B_MAX_WORKERS", "4"))

_executor = None
_executor_lock = threading.Lock()


def start_agent(job):
    global _executor
    with _executor_lock:
        if _executor is None:
            _executor = ThreadPoolExecutor(
                max_workers=MAX_WORKERS, thread_name_prefix="p2b")
    _executor.submit(run_job, job)


# ---------------------------------------------------------------- state

def _set(job, **kw):
    job.update(kw)
    if kw.get("state") in ("done", "failed"):
        job["finishedAt"] = time.time()
    (JOBS_DIR / job["jobId"]).mkdir(parents=True, exist_ok=True)
    (JOBS_DIR / job["jobId"] / "job.json").write_text(json.dumps(job, indent=2))
    print(f"[p2b] {job['jobId']} {kw.get('stage', '?')}: {kw.get('message', '')[:80]}", flush=True)


def _fail(job, msg, detail=""):
    _set(job, state="failed", stage="failed", message=msg, detail=str(detail)[:400])


# ---------------------------------------------------------------- prompts

SYSTEM_PROMPT = """You are the worker brain inside a kid-friendly game called Play2Build. \
A player picked an idea and answered a few simple questions with big buttons. \
Your job: build a small, complete, REAL project that actually runs.

Quality bar (very important):
- It must work when the player runs it. No stubs, no fake code, no placeholder \
comments, no "example" filler, no lorem ipsum.
- Complete logic, real behavior, good names. Think: a small but finished app.
- Keep it SMALL — usually 1-5 files, never more than 12, no file over 250 lines.
- Self-contained: no API keys, no network needed to run, no external services.
- Write README.md explaining what it is in plain words and how to run it.

Reply with ONLY one JSON object, no prose before or after. Shape:
{"summary": string, "files": [{"path": string, "content": string}], "run": string}
- summary: 1-2 short, plain sentences a 10-year-old understands. Caveman-simple words.
- run: how to run it in one line, e.g. "python3 main.py"."""


def build_prompt(job):
    idea = job["idea"]
    answers = {}
    for a in job["answers"]:
        if isinstance(a, dict) and a.get("id"):
            answers[a["id"]] = a.get("label") or a.get("choice") or ""
    lines = [
        f"Idea: {idea.get('name', 'a project')} — {idea.get('description', '')}",
    ]
    if answers.get("size"):
        lines.append(f"Size: {answers['size'].lower()} (tiny=1 file-ish, medium=a few files, big=bigger)")
    if answers.get("language"):
        lines.append(f"Language: {answers['language'].lower()} (if 'workers pick', choose the best)")
    if answers.get("fancy"):
        lines.append(f"Look: {answers['fancy'].lower()} (simple=clean, nice=styled, fancy=polished)")
    user = "\n".join(lines)
    return SYSTEM_PROMPT, user


# ---------------------------------------------------------------- checks

def validate(project_dir):
    """Best-effort syntax check. Returns list of error strings (empty = ok)."""
    errors = []
    py_files = list(project_dir.rglob("*.py"))
    if py_files:
        r = subprocess.run(["python3", "-m", "py_compile", *map(str, py_files)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(r.stderr.strip()[:500])
    js_files = list(project_dir.rglob("*.js"))
    if js_files:
        for f in js_files[:10]:
            r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
            if r.returncode != 0:
                errors.append(f"{f.name}: {r.stderr.strip()[:200]}")
    return errors


# ---------------------------------------------------------------- git / github

def _git(cwd, *args, timeout=120):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                       timeout=timeout, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])} failed: {r.stderr.strip()[:400]}")
    return r.stdout.strip()


def _gh(path, method="GET", payload=None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method)
    req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(payload).encode()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"github {method} {path} -> {e.code}: {e.read().decode(errors='replace')[:300]}") from e


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "project"


def push_to_github(project_dir, job, summary):
    if not GITHUB_TOKEN:
        raise RuntimeError("no GitHub token — put GITHUB_TOKEN in backend/.env")
    owner = _gh("/user").get("login")
    if not owner:
        raise RuntimeError("could not read GitHub username from token")
    name = f"{REPO_PREFIX}-{slugify(job['idea'].get('name', 'project'))}-{job['jobId'][:4]}"
    _gh("/user/repos", method="POST", payload={
        "name": name,
        "description": (summary or "Built by Play2Build.")[:120],
        "public": GITHUB_PUBLIC,
        "has_issues": False, "has_wiki": False,
    })
    _git(project_dir, "init", "-b", "main")
    _git(project_dir, "add", "-A")
    _git(project_dir, "-c", "user.name=Play2Build Bot",
         "-c", "user.email=play2build-bot@users.noreply.github.com",
         "commit", "-m", f"Build it: {summary[:100]}")
    _git(project_dir, "remote", "add", "origin",
         f"https://x-access-token:{GITHUB_TOKEN}@github.com/{owner}/{name}.git")
    try:
        _git(project_dir, "push", "-u", "origin", "main", timeout=180)
    finally:
        # never leave the token sitting in .git/config
        _git(project_dir, "remote", "remove", "origin")
    return f"https://github.com/{owner}/{name}"


# ---------------------------------------------------------------- the job

def run_job(job):
    job_id = job["jobId"]
    project_dir = JOBS_DIR / job_id / "project"
    try:
        system, user = build_prompt(job)
        _set(job, state="running", stage="planning",
             message="Planning",
             detail=f"Planning your {job['idea'].get('name', 'project')}")

        if ENGINE == "mock":
            summary = (f"We will make a tiny {job['idea'].get('name', 'project')} "
                       f"for you. It will run when you run it.")
            files = [
                {"path": "README.md", "content":
                    f"# {job['idea'].get('name', 'Project')}\n\n"
                    f"{job['idea'].get('description', '')}\n\n"
                    "Made by the Play2Build game.\n"},
                {"path": "main.py", "content":
                    f"print('Hello from the Play2Build game!')\n"
                    f"print('Your {job['idea'].get('name', 'project')} is ready.')\n"},
            ]
            cost = 0.0
        else:
            result, cost = None, 0.0
            last_err = None
            for attempt in (1, 2, 3):
                try:
                    result, cost = llm.json_call(system, user, max_tokens=12000,
                                                 extra=None if attempt == 1 else {
                                                     "instruction": "your last reply was cut "
                                                     "off / not valid JSON. Reply again with "
                                                     "the FULL JSON object. Keep every file "
                                                     "under 200 lines."})
                    break
                except Exception as e:  # bad JSON, network hiccup, etc.
                    last_err = e
                    if attempt == 1:
                        _set(job, state="running", stage="planning",
                             message="Planning (retry)", detail="")
            if result is None:
                raise RuntimeError(f"the brain could not answer: {last_err}")
            summary = str(result.get("summary", "We will build it for you."))[:300]
            files = result.get("files")
            if not isinstance(files, list) or not files:
                raise RuntimeError("the brain sent no files")

        _set(job, state="running", stage="writing",
             message="Writing code", detail=summary,
             costUsd=round(cost, 4))

        if project_dir.exists():
            shutil.rmtree(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / ".gitignore").write_text("__pycache__/\n*.pyc\n")
        for f in files:
            path = str(f.get("path") or "")
            if not path or ".." in path or path.startswith("/") or "\\" in path:
                continue
            p = project_dir / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(str(f.get("content") or ""))

        _set(job, state="running", stage="checking",
             message="Checking code", detail="")
        errors = validate(project_dir)
        if errors and ENGINE != "mock":
            _set(job, state="running", stage="checking",
                 message="Checking code (fixing)", detail="")
            try:
                result2, cost2 = llm.json_call(
                    system, user, max_tokens=8000,
                    extra={"the first attempt failed these checks": errors,
                           "instruction": "send the FIXED full file list again"})
                files2 = result2.get("files")
                if isinstance(files2, list) and files2:
                    for f in files2:
                        path = str(f.get("path") or "")
                        if not path or ".." in path or path.startswith("/") or "\\" in path:
                            continue
                        p = project_dir / path
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text(str(f.get("content") or ""))
                    job["costUsd"] = round(job.get("costUsd", 0) + cost2, 4)
                    errors = validate(project_dir)
            except Exception:
                traceback.print_exc()
        if errors:
            raise RuntimeError("project did not pass checks: " + "; ".join(str(e)[:120] for e in errors[:3]))

        _set(job, state="running", stage="pushing",
             message="Pushing to GitHub", detail="")
        repo_url = push_to_github(project_dir, job, summary)
        _set(job, state="done", stage="done",
             message="Done", detail=repo_url, repoUrl=repo_url)
    except Exception as e:
        traceback.print_exc()
        _fail(job, "Build failed", str(e)[:300])
