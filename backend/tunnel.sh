#!/usr/bin/env bash
# Open a tunnel so the Roblox game can reach this backend from anywhere.
# Prints a https://xxx.trycloudflare.com URL — paste it into
# game/src/shared/Config.lua as BACKEND_URL.
set -euo pipefail
cd "$(dirname "$0")"
exec cloudflared tunnel --url "http://127.0.0.1:${P2B_PORT:-8000}"
