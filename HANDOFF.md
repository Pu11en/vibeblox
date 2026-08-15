# HANDOFF — Play2Build v0.1 (private validation loop)

State as of 2026-08-14: **built and code-tested; not yet played by Drew.**

## What exists

- `backend/` — stdlib-only Python factory (no pip installs): serves ideas +
  questions to the game, runs the DeepSeek agent pipeline, pushes public
  repos to Drew's GitHub. Tested end-to-end with `ENGINE=mock` (everything
  works up to the GitHub push, which needs the real token).
- `game/` — Rojo project; `game/build/play2build.rbxlx` is compiled and
  verified. All Luau passes `luau-analyze` with zero errors.
- `README.md` — plain-language setup + run instructions (Steps 1-3: DeepSeek
  key, GitHub token, .env; then run + play).

## Status (updated 2026-08-15, after Drew's keys)

- **THE LOOP IS PROVEN END-TO-END.** With live keys:
  - DeepSeek key: verified ($0.00003 probe call; real builds at ~$0.0026 each).
  - GitHub token (2nd one, `Pu11en` account): verified — first real build pushed
    a live **public repo**: https://github.com/Pu11en/play2build-snake-game-3f7a
    (real Tkinter snake game, README, passed syntax check; the whole build ran
    in ~54s for $0.0026).
  - Two pipeline fixes added during live testing: (1) retry the brain call once
    if its JSON reply is truncated/invalid, with a "keep files under 200 lines"
    hint; (2) `.gitignore` (`__pycache__/`) is now written into every project
    before commit.
- Factory is running as a background task (managed by the session); if it ever
  stops: `backend/run.sh`.

## What Drew must do before the first playthrough

1. Create a DeepSeek API key (platform.deepseek.com) → paste into
   `backend/.env` (`DEEPSEEK_API_KEY=`).
2. Create a GitHub classic PAT with `repo` scope → paste into
   `backend/.env` (`GITHUB_TOKEN=`).
3. Run `backend/run.sh` in WSL; open `game/build/play2build.rbxlx` in Studio;
   tick Game Settings → Security → **Allow HTTP Requests**; press Play.
4. (Published-game only) run `backend/tunnel.sh` and set the URL in
   `game/src/shared/Config.lua`.

## Decisions made this session (fill in the open tickets)

- Bridge architecture: local WSL backend + `http://127.0.0.1:8000` from
  Studio (or Cloudflare tunnel for published play); secret header
  `X-P2B-Secret` (shared constant, fine for private validation); polling
  every 4s (500 req/min limit not a factor); DeepSeek `deepseek-v4-flash`
  (OpenAI-compatible, $0.14 in / $0.28 out per 1M tokens); GitHub classic
  PAT `repo` scope; repos named `play2build-<idea>-<id>`, public.
- Play loop: click-to-plan (idea cards → 3 A/B/C questions → build →
  progress → repo URL + fake cash). Caveman-simple language. TTS narration
  with mute. No typing anywhere except none — pure clicking.
- Validation bar (proposed): one successful playthrough producing a live
  public repo = loop proven; Drew vibe-checks "feels like play" during the
  session; latency budget ~2-3 min for small projects.

## No-Studio path (added 2026-08-15, per Drew's requirement)

- Drew should never need Studio: the game is 100% code-built here (map, UI,
  scripts via Rojo). Playing happens in the normal Roblox Player.
- `backend/publish.py` + `backend/publish.sh` publish the built place via
  the Open Cloud Place Publishing API (POST .../versions?versionType=Published).
  It injects the DataModel `HttpEnabled=true` property into the .rbxlx XML
  (verified: well-formed, idempotent) so "Allow HTTP Requests" needs no
  Studio click.
- Pending Drew: Open Cloud API key (create.roblox.com → Creator Hub →
  Credentials → API Keys, scope `universe-places` Write → backend/.env as
  `ROBLOX_API_KEY`) + universe/place IDs from a website-created experience
  (create.roblox.com → Create → Experience). Then: `./run.sh`, `./tunnel.sh`,
  `./publish.sh <tunnel-url>`, play at www.roblox.com/games/<placeId>.
- Game copy fixed: "BUILD SOMETHING" → "ASK THE WORKERS" (workers build;
  the player only requests). Rebuilt .rbxlx included.

## Known follow-ups (deferred, in order)

1. Repo-idealab idea feed (swap `backend/ideas.py` for the channel feed —
   the API seam is already there).
2. Speech-to-text input (Roblox has no official STT; research needed).
3. The public game (North Star; fresh effort).

## Copy-paste prompt for the next session

> Continue Play2Build in ~/main-projects/roblox/play2build (see README.md +
> HANDOFF.md). The private validation loop is built: WSL Python backend +
> DeepSeek agent + GitHub push, and a Roblox click-to-plan tycoon compiled
> to game/build/play2build.rbxlx. I have put my DeepSeek API key and GitHub
> token in backend/.env. Run backend/run.sh, then open the .rbxlx in Studio
> (Game Settings → Security → Allow HTTP Requests) and play a round: pick an
> idea, answer the questions, confirm a public play2build-* repo appears on
> my GitHub, and tell me how it felt. Fix whatever breaks.
