"""Daily scraper: pull new @GithubAwesome videos into the repo database.

Newest-video detection via the channel RSS feed (verified in the money
signals research). For each video not yet stored: fetch the description with
yt-dlp, extract github.com/owner/repo links, insert idempotently. Videos
without repo links (clips, tutorials) are recorded and skipped.
"""

from __future__ import annotations

import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import httpx

from gitbutt.db import connect

CHANNEL_ID = "UC9Rrud-8CaHokDtK9FszvRg"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
WATCH_URL = "https://www.youtube.com/watch?v={id}"
GITHUB_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")
YT_NS = {"yt": "http://www.youtube.com/xml/schemas/2015"}


def rss_entries() -> list[dict]:
    """Newest-first video entries from the channel RSS feed."""
    resp = httpx.get(RSS_URL, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    entries = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        video_id = entry.findtext("yt:videoId", namespaces=YT_NS)
        title = entry.findtext("{http://www.w3.org/2005/Atom}title")
        published = entry.findtext("{http://www.w3.org/2005/Atom}published")
        if video_id:
            entries.append({"video_id": video_id, "title": title or "", "published": published or ""})
    return entries


def fetch_description(video_id: str) -> str:
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
        check=False,
    )
    return proc.stdout if proc.returncode == 0 else ""


def extract_repos(description: str) -> list[str]:
    repos = []
    for match in GITHUB_RE.finditer(description or ""):
        repo = match.group(1).rstrip("/.,;)")
        if repo.count("/") == 1:
            repos.append(repo)
    return list(dict.fromkeys(repos))


def scrape() -> dict:
    conn = connect()
    try:
        entries = rss_entries()
        seen = {
            r["video_id"]
            for r in conn.execute("SELECT video_id FROM videos").fetchall()
        }
        new_videos = [e for e in entries if e["video_id"] not in seen]
        added_videos = 0
        added_repos = 0
        no_links: list[str] = []
        for entry in new_videos:
            description = fetch_description(entry["video_id"])
            repos = extract_repos(description)
            conn.execute(
                "INSERT OR REPLACE INTO videos (video_id, title, description) VALUES (?, ?, ?)",
                (entry["video_id"], entry["title"], description),
            )
            for full_name in repos:
                owner, name = full_name.split("/", 1)
                conn.execute(
                    "INSERT OR IGNORE INTO repos (full_name, owner, name, first_seen_video) "
                    "VALUES (?, ?, ?, ?)",
                    (full_name, owner, name, entry["video_id"]),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO video_repos (video_id, full_name) VALUES (?, ?)",
                    (entry["video_id"], full_name),
                )
                added_repos += 1
            if not repos:
                no_links.append(entry["title"])
            added_videos += 1
            conn.commit()
        return {
            "feed_size": len(entries),
            "already_known": len(seen),
            "new_videos": len(new_videos),
            "videos_added": added_videos,
            "repos_added": added_repos,
            "no_link_videos": no_links,
        }
    finally:
        conn.close()
