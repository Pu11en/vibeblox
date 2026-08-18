# What is the game → backend → GitHub bridge architecture?

> `wayfinder:grilling` — child ticket of the map. Created 2026-08-02.
> **CLOSED 2026-08-14** — resolved by building the actual thing (v0.1).

## Resolution

Built and code-tested as `play2build/` (backend + game + README). The
architecture, as shipped:

- **Transport:** the game POSTs `/api/start` and POLLs `/api/status?job=`
  every 4s from server-side HttpService (well under the 500 req/min cap).
  Push (Open Cloud `publishMessage`) deferred — polling is simpler, works in
  Studio, and needs no Open Cloud key. Swap later if latency hurts.
- **Host:** local WSL Python backend (stdlib-only, no deps), reachable from
  Studio as `http://127.0.0.1:8000` via WSL localhost forwarding; Cloudflare
  quick tunnel (`backend/tunnel.sh`) for published play. No VPS for v0.1.
- **Auth:** shared secret header `X-P2B-Secret` (constant in
  `game/src/shared/Config.lua` + `backend/.env`) — fine for a private loop;
  the backend is the only holder of the GitHub token, so the shape survives
  the future GitHub-OAuth upgrade.
- **Agent invocation & repo push:** DeepSeek `deepseek-v4-flash`
  (OpenAI-compatible, $0.14/$0.28 per 1M in/out) generates the whole project
  as JSON; backend writes files, syntax-checks (py_compile / node --check,
  one auto-fix retry), `git init`+commit, creates the repo via GitHub REST
  (classic PAT, `repo` scope), pushes, and strips the token from the remote.
- **Progress surface:** `/api/status` returns `{state, stage, message,
  detail, repoUrl, costUsd, elapsedMs}`; the game maps stage → progress bar
  and shows plain-language messages.
- Per-run cost tracked (pricing input for the future public game).

Full run instructions: `play2build/README.md`. Keyed by: the game → backend
Hop stays local-first; the tunnel is a one-liner.

Blocked by: [What can a Roblox game integrate with externally?](roblox-external-integration-capabilities.md)
and [Which agent engine powers the backend?](agent-engine-and-cost.md).
