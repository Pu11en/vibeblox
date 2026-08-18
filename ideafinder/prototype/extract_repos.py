"""Prototype: extract GitHub repos from @GithubAwesome video descriptions.

Verified 2026-07-31: every repo list video carries full github.com/owner/repo
URLs in its description, so extraction is a regex over the description.

Usage:
    uv run python prototype/extract_repos.py sample <video_id> [video_id ...]
    uv run python prototype/extract_repos.py backfill
    uv run python prototype/extract_repos.py selftest
"""

from __future__ import annotations

import re
import sqlite3
import subprocess
import sys
from pathlib import Path

BRAIN_DB = Path(
    r"C:\Users\drewp\AppData\Local\channel-brains-mcp\channel-brains-mcp\channel_brains.sqlite3"
)
REPO_DB = Path(__file__).resolve().parent.parent / "data" / "repos.sqlite3"
WATCH_URL = "https://www.youtube.com/watch?v={id}"
GITHUB_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")


def brain_videos() -> list[dict[str, str]]:
    """All videos the channel brain indexed, in channel position order."""
    conn = sqlite3.connect(BRAIN_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT video_id, title FROM videos ORDER BY position").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_description(video_id: str) -> str:
    """One yt-dlp call per video, description only, no download."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "yt_dlp",
            "--skip-download",
            "--no-warnings",
            "--print",
            "%(description)s",
            WATCH_URL.format(id=video_id),
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def extract_repos(description: str) -> list[str]:
    """Full github.com/owner/repo URLs, deduped, order preserved."""
    repos = []
    for match in GITHUB_RE.finditer(description or ""):
        repo = match.group(1).rstrip("/.,;)")
        if repo.count("/") == 1:
            repos.append(repo)
    return list(dict.fromkeys(repos))


def init_repo_db() -> sqlite3.Connection:
    REPO_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(REPO_DB)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS repos (
            full_name TEXT PRIMARY KEY,
            owner TEXT NOT NULL,
            name TEXT NOT NULL,
            first_seen_video TEXT,
            first_seen_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS video_repos (
            video_id TEXT NOT NULL REFERENCES videos(video_id),
            full_name TEXT NOT NULL REFERENCES repos(full_name),
            PRIMARY KEY (video_id, full_name)
        );
        """
    )
    conn.commit()
    return conn


def cmd_sample(video_ids: list[str]) -> int:
    for video_id in video_ids:
        description = fetch_description(video_id)
        repos = extract_repos(description)
        print(f"\n=== {video_id} ({len(repos)} repos) ===")
        for repo in repos:
            print(f"  {repo}")
    return 0


def cmd_backfill() -> int:
    videos = brain_videos()
    conn = init_repo_db()
    total_repos = 0
    no_link_videos = []
    for i, video in enumerate(videos, start=1):
        video_id = video["video_id"]
        title = video["title"]
        repos = extract_repos(fetch_description(video_id))
        conn.execute(
            "INSERT OR REPLACE INTO videos (video_id, title) VALUES (?, ?)", (video_id, title)
        )
        if not repos:
            no_link_videos.append(title)
            print(f"[{i}/{len(videos)}] {video_id} 0 repos: {title[:60]}")
            continue
        for full_name in repos:
            owner, name = full_name.split("/", 1)
            conn.execute(
                "INSERT OR IGNORE INTO repos (full_name, owner, name, first_seen_video) "
                "VALUES (?, ?, ?, ?)",
                (full_name, owner, name, video_id),
            )
            conn.execute(
                "INSERT OR IGNORE INTO video_repos (video_id, full_name) VALUES (?, ?)",
                (video_id, full_name),
            )
        total_repos += len(repos)
        print(f"[{i}/{len(videos)}] {video_id} {len(repos)} repos: {title[:60]}")
        conn.commit()
    conn.commit()
    conn.close()
    print(f"\nDone. {len(videos)} videos, {total_repos} repo mentions, "
          f"{len(no_link_videos)} videos with no links.")
    for title in no_link_videos:
        print(f"  no links: {title[:80]}")
    return 0


def cmd_selftest() -> int:
    """Offline checks: dedupe, junk stripping, link filtering, empty input."""
    sample = (
        "00:00 Intro\n"
        "01:00 Repo A https://github.com/octo/kit\n"
        "02:00 Repo B https://github.com/octo/kit\n"
        "03:00 Dot https://github.com/acme/widget.\n"
        "04:00 Bad https://github.com/owner\n"
        "05:00 Sponsor https://example.com/x\n"
    )
    expected = ["octo/kit", "acme/widget"]
    got = extract_repos(sample)
    assert got == expected, f"expected {expected}, got {got}"
    assert extract_repos("no links here") == []
    assert extract_repos("") == []
    print(f"SELFTEST OK: {got}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    command, rest = args[0], args[1:]
    if command == "sample":
        if not rest:
            print("sample needs at least one video id")
            return 1
        return cmd_sample(rest)
    if command == "backfill":
        return cmd_backfill()
    if command == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
