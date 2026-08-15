# HANDOFF — Play2Build (state as of 2026-08-15, ~02:30)

## Where we are

**The machine is built and the dev loop works.** The game runs in Studio
via Rojo live-sync: I edit `.luau` in WSL → it lands in Studio in seconds
→ Drew presses Esc+F5 and sees it. This session's goal ("set up so I can
build everything for you") is achieved.

**Verified working end-to-end:**
- Factory: real DeepSeek build → syntax check → public GitHub repo push
  (proof: https://github.com/Pu11en/play2build-snake-game-3f7a, ~$0.0026/job).
- Live sync: Rojo plugin installed in Drew's Studio, connected to
  `rojo serve` (port 34872), welcome signboard built live in front of him.
- Experience released: universe `10708566177`, place `133497593239683`,
  PUBLIC + indexed (games API shows name + rootPlaceId). Uploads land
  (versions increment) — but the LINK has never shown the game (sky).
- Git: repo initialized at `play2build/` (first commit `64bb4bd`), `.env`
  and build artifacts gitignored.

## Open items (next session, in order)

1. **P1 — The published link still shows sky.** Everything local works;
   the experience is released; uploads land but the link serves an empty
   world. Remaining theories: (a) the Open Cloud uploads were all made
   while the experience was PRIVATE and the pre-release versions are what
   the link serves — since release, uploads have 409'd ("Server is busy",
   ~90s+ retry gaps clear it — the old 3-min retry loop broke through after
   ~45 min); (b) the HttpEnabled injection wrapper breaks server loading
   (untested in isolation). Action: with the experience now PUBLIC, get ONE
   upload through (Workspace-fixed build is ready in `game/build/`) and
   check the link. If sky persists, publish a NON-injected version to split
   theory (b); if still sky, create a fresh experience (dashboard) and
   publish to it. Do NOT re-litigate the local loop — it works.
2. **P2 — Start the real build.** Drew wants to build the actual game now
   (his words: "now we need to start to actually build what we want to
   build"). The tycoon skeleton + click-to-plan flow exist; the fun
   iteration starts (idea cards, questions, worker bots, economy feel).
3. **P3 — Repo-idealab idea feed** (backend/ideas.py swap).

## How to resume (Drew's side)

1. WSL: `cd ~/main-projects/roblox/play2build && ./dev.sh`
2. Studio: Plugins → Rojo → Connect (localhost:34872)
3. F5 to play, Esc+F5 to see changes.

## Secrets (gitignored, in backend/.env)

DeepSeek API key, GitHub PAT (repo scope), Roblox Open Cloud key
(Places/Universes/DataStores/Messaging/Assets/Economy read+write).
P2B_SECRET=dev-secret-change-me (dev only — matches Config.lua).
Rotate the GitHub token someday: it was pasted in chat early on.

## Copy-paste prompt for the next session

> Continue Play2Build in ~/main-projects/roblox/play2build (README.md +
> HANDOFF.md). The dev loop works: ./dev.sh brings up factory + tunnel +
> rojo serve; Drew's Studio is connected via the Rojo plugin; I edit Luau
> here and he sees it live. P1: the published link
> (https://www.roblox.com/games/133497593239683) still shows an empty sky
> even though the experience is released and uploads land — get one upload
> through (the Workspace-fixed build is in game/build/, retry with 90s+
> gaps on 409s) and verify the link; if still sky, publish a non-injected
> version, then try a fresh experience. P2 after that: start the real game
> build with Drew (he wants to play-build the actual game now). Keys are in
> backend/.env (gitignored). Don't touch planning/ or AGENTS.md.
