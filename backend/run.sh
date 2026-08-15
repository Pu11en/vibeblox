#!/usr/bin/env bash
# Start the Play2Build factory. Ctrl-C to stop.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 server.py
