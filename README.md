# VibeBlox — plan-first build machine

> Repo: https://github.com/Pu11en/vibeblox (public) · Local: `~/main-projects/vibeblox`

You pick an idea card, answer three easy A/B/C questions with big buttons,
and **real workers** (an AI brain on a real backend) write a real, working
project and push it to your GitHub as a **public repo**. In the game it
feels like a tycoon: worker bots hop around, the vault flashes green, and
you get paid fake cash for real work.

```
YOU (in Roblox)  --click-->  idea card + 3 answers
      |                              |
      v                              v
  Roblox server (Luau)  --HTTP-->  Factory (WSL, Python)
                                     |  DeepSeek brain writes the code
                                     |  checks it runs (python/node syntax)
                                     |  git init + commit
                                     v
                                 GitHub (public repo: play2build-*)
      ^                              |
      |<-- polls status every 4s ----+
```

## The dev loop — how we work (LIVE SYNC)

The whole game is code-built in WSL (map, UI, everything). Changes flow
into Studio instantly, no rebuilding, no new files.

**One-time setup (done 2026-08-15):** the Rojo plugin is installed in
Studio (Plugins tab → Rojo → Connect to `localhost:34872`).

**Every session:**

```bash
cd ~/main-projects/vibeblox
./dev.sh          # starts factory + tunnel + live-sync server (safe to re-run)
```

Then in Studio: **Plugins → Rojo → Connect** (or it auto-connects).
The game appears in the editor. To play: **F5**. To see changes:
**Esc, then F5** — the file never needs closing.

I edit a `.luau` file in WSL → it lands in Studio within a second →
you press Esc+F5 → you see it. That's the whole loop.

## One-time keys (already in backend/.env)

- `DEEPSEEK_API_KEY` — the brain (platform.deepseek.com)
- `GITHUB_TOKEN` — repo delivery (github.com/settings/tokens, classic, `repo` scope)
- `ROBLOX_API_KEY` — publishing (create.roblox.com → Creator Hub → Credentials → API Keys;
  scopes: Places, Universes, Data Stores, Messaging, Assets, Economy — read+write)
- `P2B_SECRET` — shared secret between the game and the factory (must match
  `game/src/shared/Config.lua`)

## Publishing (secondary — the dev loop is primary)

The experience exists and is **released**: universe `10708566177`,
place `133497593239683`, game link https://www.roblox.com/games/133497593239683

```bash
cd ~/main-projects/vibeblox/backend
./tunnel.sh                          # print the https://xxx.trycloudflare.com URL
./publish.sh https://xxx.trycloudflare.com   # patches Config, builds, uploads
```

Note: the Open Cloud upload endpoint is flaky ("Save failed. Server is
busy") — retry with ~90s+ gaps; it clears. `publish.py` remembers the
experience IDs after the first run.

## What's in the folder

| Path | What it is |
|------|-----------|
| `game/` | The Roblox game (Rojo project, Luau source — THE source of truth) |
| `game/src/server/` | Map build, job polling, idea fetching (`.server.lua` = server scripts) |
| `game/src/client/` | The terminal UI, HUD, TTS, economy (`.client.lua` = client scripts) |
| `game/src/shared/` | Config (backend URL, secret) + remotes |
| `backend/` | The factory: Python HTTP server + DeepSeek agent + GitHub pusher (stdlib only) |
| `backend/.env` | Your keys (gitignored — never commit) |
| `dev.sh` | One command: factory + tunnel + live-sync up |

## How the workers build (and what it costs)

Pipeline per build: **plan** → **write files** → **check it runs**
(py_compile / node --check, one auto-fix retry; brain retries once on
truncated replies) → **git commit** → **create public repo**
`play2build-<idea>-xxxx` → **push**. Cost tracked per job
(DeepSeek v4-flash: $0.14 / 1M input, $0.28 / 1M output — a small project
costs a fraction of a cent).

## Testing without keys (mock mode)

```bash
echo "ENGINE=mock" >> backend/.env && cd backend && ./run.sh
```

Builds a hello-world repo with no AI. Jobs still fail at the push step
until `GITHUB_TOKEN` is set — that's expected.

## Roadmap (deferred)

- Repo-idealab idea feed (swap `backend/ideas.py` for the channel feed —
  the `/api/ideas` seam is already there).
- Speech-to-text input (Roblox has no official STT; research needed).
- The public game (other players, credits economy) — the North Star.
