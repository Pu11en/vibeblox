#!/usr/bin/env python3
"""Play2Build backend — the game's factory.

Stdlib-only HTTP server. Endpoints:
  GET  /health                       -> {"ok": true}
  GET  /api/ideas                    -> idea cards for the game
  GET  /api/questions                -> planning questions (A/B/C)
  POST /api/start   {idea, answers}  -> {"jobId": "..."}
  GET  /api/status?job=ID            -> job snapshot for the game

Auth: every /api/* request must carry header X-P2B-Secret matching P2B_SECRET.
"""
import json
import os
import threading
import time
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOBS_DIR = ROOT / "jobs"


def load_env():
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


load_env()

SECRET = os.environ.get("P2B_SECRET", "dev-secret-change-me")
PORT = int(os.environ.get("P2B_PORT", "8000"))
ENGINE = os.environ.get("ENGINE", "deepseek")

from ideas import IDEAS  # noqa: E402
from questions import QUESTIONS  # noqa: E402
import agent  # noqa: E402
import llm  # noqa: E402

jobs = {}
jobs_lock = threading.Lock()


def job_snapshot(job_id):
    with jobs_lock:
        j = jobs.get(job_id)
        if not j:
            return None
        elapsed = None
        start = j.get("startedAt") or j.get("createdAt")
        if start is not None:
            end = j.get("finishedAt") or time.time()
            elapsed = int((end - start) * 1000)
        return {
            "jobId": j["jobId"],
            "state": j.get("state"),
            "stage": j.get("stage"),
            "message": j.get("message", ""),
            "detail": j.get("detail", ""),
            "repoUrl": j.get("repoUrl"),
            "costUsd": j.get("costUsd", 0.0),
            "elapsedMs": elapsed,
            "runCommand": j.get("runCommand", ""),
            "idea": j.get("idea", {}).get("name", ""),
        }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[http] " + (fmt % args), flush=True)

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/health":
            return self._send(200, {"ok": True, "engine": ENGINE})
        if self.headers.get("X-P2B-Secret") != SECRET:
            return self._send(401, {"error": "bad secret"})
        if path == "/api/ideas":
            return self._send(200, {"ideas": IDEAS})
        if path == "/api/questions":
            return self._send(200, {"questions": QUESTIONS})
        if path == "/api/status":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1])
            snap = job_snapshot(qs.get("job", [""])[0])
            if not snap:
                return self._send(404, {"error": "no such job"})
            return self._send(200, snap)
        self._send(404, {"error": "no such route"})

    def do_POST(self):
        if self.headers.get("X-P2B-Secret") != SECRET:
            return self._send(401, {"error": "bad secret"})
        path = self.path.split("?")[0]
        if path != "/api/start":
            return self._send(404, {"error": "no such route"})
        length = int(self.headers.get("Content-Length", 0) or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._send(400, {"error": "bad json"})
        idea = body.get("idea")
        answers = body.get("answers") or []
        if not isinstance(idea, dict) or not idea.get("id"):
            return self._send(400, {"error": "missing idea"})
        job = {
            "jobId": uuid.uuid4().hex[:12],
            "idea": idea,
            "answers": answers,
            "player": str(body.get("playerName") or "player")[:40],
            "state": "queued",
            "stage": "queued",
            "message": "Queued",
            "detail": "",
            "repoUrl": None,
            "costUsd": 0.0,
            "createdAt": time.time(),
            "startedAt": None,
            "finishedAt": None,
        }
        with jobs_lock:
            jobs[job["jobId"]] = job
        agent.start_agent(job)
        return self._send(200, {"jobId": job["jobId"]})


def main():
    JOBS_DIR.mkdir(exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    secret_note = "set" if SECRET != "dev-secret-change-me" else "DEFAULT - change me!"
    keys_note = "deepseek=" + ("SET" if llm.API_KEY else "MISSING") \
        + " github=" + ("SET" if agent.GITHUB_TOKEN else "MISSING")
    print(f"[p2b] factory open at http://127.0.0.1:{PORT} engine={ENGINE} "
          f"secret={secret_note} keys: {keys_note}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
