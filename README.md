# Play2Build — the game where playing IS building

You pick an idea card, answer three easy A/B/C questions with big buttons,
and **real workers** (an AI brain on a real backend) write a real, working
project and push it to your GitHub as a **public repo**. In the game it
feels like a tycoon: workers hop around, the vault flashes green, and you
get paid fake cash for real work.

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

## What was built (all in this folder)

| Path | What it is |
|------|-----------|
| `backend/` | The factory: Python HTTP server + DeepSeek agent + GitHub pusher (no installs needed, pure stdlib) |
| `backend/.env` | Your keys go here (copy of `.env.example`) |
| `game/` | The Roblox tycoon as a Rojo project (Luau source) |
| `game/build/play2build.rbxlx` | **The ready-to-open place file** — open this in Studio, no plugins needed |
| `HANDOFF.md` | Notes for the next dev session |

## Setup — 3 steps, then play

### Step 1: DeepSeek key (the brain)
1. Go to https://platform.deepseek.com and sign in (or create an account).
2. Top up a little money (a few dollars lasts a long time — one build costs
   pennies).
3. Create an API key (API Keys → Create). Copy it.

### Step 2: GitHub token (the delivery)
1. Go to https://github.com/settings/tokens → **Generate new token (classic)**.
2. Tick the **`repo`** scope (that's the whole "repo" checkbox group).
3. Generate, copy it. It looks like `ghp_...`.

### Step 3: Put the keys in
1. In WSL, open `play2build/backend/.env` (it's already there).
2. Paste the DeepSeek key after `DEEPSEEK_API_KEY=`.
3. Paste the GitHub token after `GITHUB_TOKEN=`.
4. Optional: change `P2B_SECRET` to anything (write it down — it must match
   the game's `Config.lua` too, see below).

## Run it

In WSL (two terminals):

```bash
# Terminal 1: start the factory
cd ~/main-projects/roblox/play2build/backend
./run.sh

# Terminal 2 (only needed if you play on a published game, not in Studio):
./tunnel.sh
# -> copy the https://xxx.trycloudflare.com URL
```

## Play it — the NO-Studio way (recommended)

You never need Roblox Studio for anything. One-time website setup (~5 min),
then everything is automated from WSL:

1. **Make an API key (website, not Studio):** go to create.roblox.com →
   sign in → your avatar menu → **Creator Hub** → **Credentials** → **API
   Keys** → Create Key. Name it anything; scopes: **universe-places** with
   **Write**. Copy the key into `backend/.env` as `ROBLOX_API_KEY=`.
2. **Make the experience (website, not Studio):** create.roblox.com →
   **Create** → **Experience** (any template). Open it → the page URL has
   the IDs, e.g. `create.roblox.com/dashboard/creations/experiences/1234/places/5678/configure`
   → note the two numbers (universe `1234`, place `5678`).
3. Start the factory + tunnel (two WSL terminals, keep them open):
   ```bash
   cd ~/main-projects/roblox/play2build/backend
   ./run.sh
   ./tunnel.sh   # prints https://xxx.trycloudflare.com
   ```
4. Publish the game (one command):
   ```bash
   ./publish.sh https://xxx.trycloudflare.com   # paste the tunnel URL
   ```
5. Open the game link it prints (`https://www.roblox.com/games/<placeId>`)
   and press **Play** in your browser — it launches in the normal Roblox
   Player. Ask the workers, answer the questions, collect your repo.

Re-publishing after changes is just step 4 again (IDs are remembered).
If the tunnel URL changes, re-run step 4 with the new URL.

## Play it — Studio way (optional, for fast local iteration)

1. Open **Roblox Studio** → open `WSL: ~/main-projects/roblox/play2build/game/build/play2build.rbxlx`
   (the WSL filesystem shows as `\\wsl.localhost\Ubuntu\home\drewp\main-projects\...`).
2. **One-time setting:** press **F4** (or Home tab → **Game Settings**) →
   **Security** tab → tick **"Allow HTTP Requests"** → OK. (The game also
   tries to enable it itself in Studio; only needed if you see a warning.)
3. Press **Play** with `backend/run.sh` running (the game reaches the
   factory at `http://127.0.0.1:8000` — set in `game/src/shared/Config.lua`).

If the game can't reach the factory (toast says "Can't reach the factory"):
- The backend must be running in WSL, and
- `game/src/shared/Config.lua` → `BackendUrl` must point at it:
  - Testing in Studio: `http://127.0.0.1:8000` (WSL localhost forwarding).
  - Published game: the tunnel URL (via `publish.sh`).

Then rebuild the place file:

```bash
cd ~/main-projects/roblox/play2build/game
rojo build default.project.json -o build/play2build.rbxlx
```

(If you use the Rojo plugin in Studio you can skip rebuilding: `rojo serve`
in `game/` and connect. The built file is the zero-plugin path.)

## What the workers do (and cost)

Pipeline per build: **plan** → **write files** → **check it runs**
(python `py_compile` / node `--check`, one auto-fix attempt) → **git commit**
→ **create public repo** `play2build-<idea>-xxxx` on your GitHub → **push**.

Cost is tracked per job (DeepSeek: $0.14 / 1M input tokens, $0.28 / 1M
output). A small project costs fractions of a cent.

## Testing without keys (mock mode)

To see the whole loop without spending anything:

```bash
cd ~/main-projects/roblox/play2build/backend
echo "ENGINE=mock" >> .env
./run.sh
```

The factory builds a hello-world repo with no AI. Jobs still fail at the
push step until `GITHUB_TOKEN` is set — that's expected.

## Changing the game without rebuilding everything

- **Ideas & questions**: edit `backend/ideas.py` and `backend/questions.py`
  (the game downloads them from the factory on startup; the built-in list in
  `game/src/shared/Config.lua` is just the offline fallback).
- **Economy numbers**: `game/src/shared/Config.lua` → `Economy`.
- **Voice**: the game already reads progress out loud (Roblox TTS, mute
  button top-right). Speech-to-text (you talk, it listens) is a v2 item —
  the plumbing is ready for it.

## Known v2 ideas (deliberately deferred)

- Pull daily ideas from the **repo-idealab** YouTube channel (the
  `GET /api/ideas` endpoint is the seam — swap the static list for the
  channel feed).
- Voice input, more workers/upgrades, in-game link copy.
- The public game (other players, credits economy) — the North Star, a
  fresh effort.
