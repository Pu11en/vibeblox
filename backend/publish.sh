#!/usr/bin/env bash
# One command: point the game at the tunnel, build, publish to Roblox.
# Usage:
#   ./publish.sh https://your-tunnel-url.trycloudflare.com
# (Requires ROBLOX_API_KEY in backend/.env; remembers universe/place IDs.)
set -euo pipefail
cd "$(dirname "$0")"

URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "Usage: ./publish.sh https://tunnel-url.trycloudflare.com"
  echo "(Get the URL from ./tunnel.sh while the factory is running.)"
  exit 1
fi

# point the game at the tunnel
sed -i "s|BackendUrl = \"[^\"]*\"|BackendUrl = \"$URL\"|" ../game/src/shared/Config.lua
echo "game -> $URL"

# build the place file
( cd ../game && rojo build default.project.json -o build/play2build.rbxlx )

# publish (IDs remembered after the first run)
python3 publish.py
