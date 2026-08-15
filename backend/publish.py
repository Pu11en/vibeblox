#!/usr/bin/env python3
"""Publish the built game to Roblox via Open Cloud — no Studio involved.

Usage:
  python3 publish.py --universe <UNIVERSE_ID> --place <PLACE_ID> [--key <API_KEY>]

Reads the built place file (game/build/play2build.rbxlx), injects the
"Allow HTTP Requests" flag into it, and uploads it as a new Published
version. IDs are remembered in backend/publish_state.json so later
publishes only need `python3 publish.py`.

API key: create.roblox.com -> avatar -> Creator Hub -> Credentials -> API Keys
Scope: "universe-places" with Write. Put it in .env as ROBLOX_API_KEY.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAME = ROOT.parent / "game"
PLACE_FILE = GAME / "build" / "play2build.rbxlx"
STATE_FILE = ROOT / "publish_state.json"

PUBLISH_URL = "https://apis.roblox.com/universes/v1/{universe}/places/{place}/versions?versionType=Published"


def load_env():
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def inject_http_enabled(xml: str) -> str:
    """Add the DataModel HttpEnabled=true property (Studio stores it there)."""
    if '<bool name="HttpEnabled">' in xml:
        return xml
    # renumber existing referents so the new DataModel can take referent 0
    counter = [0]

    def bump(m):
        counter[0] += 1
        return f'referent="{counter[0]}"'

    xml = re.sub(r'referent="(\d+)"', bump, xml)
    dm = ('<Item class="DataModel" referent="0">\n'
          '    <Properties>\n'
          '      <bool name="HttpEnabled">true</bool>\n'
          '    </Properties>\n'
          '  ')
    # the DataModel wraps the whole document (as in Studio-saved files)
    xml = xml.replace('<roblox version="4">', '<roblox version="4">\n  ' + dm, 1)
    xml = xml.replace('</roblox>', '  </Item>\n</roblox>', 1)
    return xml


def publish(universe, place, key, xml: str):
    req = urllib.request.Request(
        PUBLISH_URL.format(universe=universe, place=place),
        data=xml.encode(), method="POST")
    req.add_header("x-api-key", key)
    req.add_header("Content-Type", "application/xml")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode(errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:500]


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe", help="experience/universe ID")
    ap.add_argument("--place", help="place ID")
    ap.add_argument("--key", default=os.environ.get("ROBLOX_API_KEY", ""))
    ap.add_argument("--place-file", default=str(PLACE_FILE))
    args = ap.parse_args()

    if not args.key:
        print("ERROR: no API key — set ROBLOX_API_KEY in backend/.env "
              "(create.roblox.com -> Creator Hub -> Credentials -> API Keys)")
        return 1

    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    universe = args.universe or state.get("universeId")
    place = args.place or state.get("placeId")
    if not universe or not place:
        print("ERROR: need --universe and --place (or run once with them; IDs are remembered)")
        print("Get them from create.roblox.com -> your experience page URL.")
        return 1

    if not Path(args.place_file).exists():
        print(f"ERROR: {args.place_file} missing — run rojo build first")
        return 1
    xml = Path(args.place_file).read_text(encoding="utf-8")
    xml = inject_http_enabled(xml)
    if "HttpEnabled" not in xml:
        print("WARNING: HttpEnabled injection failed — the game needs it enabled in "
              "Experience Settings -> Security -> Allow HTTP Requests")
    status, body = publish(universe, place, args.key, xml)
    print(f"publish -> HTTP {status}: {body[:300]}")
    if status in (200, 202, 201):
        state["universeId"] = universe
        state["placeId"] = place
        STATE_FILE.write_text(json.dumps(state, indent=2))
        print(f"OK! Remembered IDs in {STATE_FILE.name}. Game link: "
              f"https://www.roblox.com/games/{place}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
