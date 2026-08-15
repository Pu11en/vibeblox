#!/usr/bin/env bash
# One command to bring up the whole dev environment:
#   factory (backend) + tunnel + rojo live-sync server
# Run this in WSL, then connect Studio via the Rojo plugin (Plugins -> Rojo -> Connect).
set -euo pipefail
cd "$(dirname "$0")"

# 1. the factory (the AI backend)
if curl -s -m 2 http://127.0.0.1:8000/health > /dev/null 2>&1; then
  echo "[dev] factory already running"
else
  echo "[dev] starting factory..."
  ( cd backend && python3 server.py > /tmp/p2b.log 2>&1 & )
  sleep 1
fi

# 2. the tunnel (only needed for the PUBLISHED game; harmless locally)
if grep -q "trycloudflare.com" /tmp/tunnel.log 2>/dev/null; then
  echo "[dev] tunnel already running"
else
  echo "[dev] starting tunnel..."
  ( cloudflared tunnel --url http://127.0.0.1:8000 > /tmp/tunnel.log 2>&1 & )
  sleep 6
  URL=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" /tmp/tunnel.log | head -1)
  echo "[dev] tunnel URL: ${URL:-starting...}"
fi

# 3. the live-sync server
if curl -s -m 2 http://127.0.0.1:34872/ > /dev/null 2>&1; then
  echo "[dev] rojo serve already running"
else
  echo "[dev] starting rojo serve..."
  ( cd game && rojo serve default.project.json > /tmp/rojo-serve.log 2>&1 & )
  sleep 2
fi
echo "[dev] ready - connect Studio: Plugins -> Rojo -> Connect (localhost:34872)"
