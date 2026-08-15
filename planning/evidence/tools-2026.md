# Tools research — how we get better at building (2026-08-15)

Research for: the one-shot build workflow of Play2Build. Each finding lists
source, what it changes, and tier.

## Tier 1 — adopt now (biggest level-up for our build)

### 1. Fusion — UI framework (our weakest link today)
- What: declarative reactive UI library for Roblox/Luau (SolidJS-inspired),
  with built-in state, tweens, springs. The community's favored UI framework
  in 2026 (ahead of Roact; "Fluid" is an emerging 2026 alternative).
- Why it matters: our in-game UI (idea cards, questions, shop, HUD) is
  hand-rolled GUI code — slow to write well, and the weakest part of the
  game. Fusion makes screens declarative + animated → better-looking game,
  faster one-shot builds.
- Sources: https://elttob.uk/Fusion/0.1/ , https://github.com/EncryptedEthan/Fusion/ ,
  https://github.com/ffrostfall/fluid (alternative)

### 2. Selene + StyLua — linter + formatter (quality gates)
- What: Selene lints Luau with Roblox API knowledge; StyLua is "Prettier for
  Luau" with `--check` for CI. Standard in every 2026 professional setup.
- Why: one-shot builds land clean; CI-style checks catch mistakes before
  Drew ever presses F5.
- Sources: https://kampfkarren.github.io/selene/ , https://github.com/JohnnyMorganz/StyLua

### 3. Rokit — toolchain version manager
- What: pins Rojo/Selene/StyLua/Wally/Lune versions per project via
  `rokit.toml` (replaced the abandoned Aftman/Foreman; Aftman archived).
- Why: the toolchain becomes reproducible — any session, any machine, same
  versions. We've been installing binaries manually.
- Sources: https://github.com/rojo-rbx/rokit

## Tier 2 — workflow upgrades (adopt when useful)

### 4. Argon — two-way live sync (Rojo-compatible, active 2026, v2.0.x)
- What: Studio↔files two-way sync for scripts AND non-script instances;
  100% Rojo project compatible. Two-way sync is OFF by default (data-loss
  safety); "porting" both directions with one button.
- Why: Drew could tweak things in Studio and they'd flow back to the repo;
  also a candidate to replace `rojo serve` later. Needs care: two-way can
  clobber files.
- Sources: https://github.com/argon-rbx/argon-roblox , https://argon.wiki/api/project

### 5. Wally — package manager (needed to install Fusion)
- What: npm-for-Roblox (wally.run); `wally install` → Packages/ synced to
  ReplicatedStorage. (pesde is an emerging second option.)
- Why: without it, we vendor Fusion by hand.
- Sources: https://wally.run , https://github.com/UpliftGames/wally

### 6. Lune + TestEZ — headless testing
- What: run Luau outside Studio (Lune) + TestEZ test framework; 2026
  templates even mock the Roblox API for full headless CI.
- Why: the factory logic (economy, job flow, question flow) gets automated
  tests → one-shot builds verified before handoff.
- Sources: https://lune-org.github.io/docs , https://github.com/Roblox/testez

## Tier 3 — asset pipeline (when the game needs custom art)

### 7. Tarmac — automated asset uploads
- What: Roblox's CLI asset manager: `tarmac sync --target roblox` uploads
  FBX/PNG and generates Lua with `rbxassetid://` refs; pairs with Rojo + CI.
- Sources: https://github.com/Roblox/tarmac

### 8. Blender headless — model generation from WSL
- What: `blender --background --python` → FBX into assets/models → Tarmac.
  Proven pipeline (smash-showdown example).
- Sources: https://github.com/bedwards/smash-showdown/issues/54

### 9. Meshy — AI 3D generation with a Roblox bridge
- What: text/image → textured 3D, GLB export, Remesh to Roblox triangle
  limits (batch ~10K / single ~21K), Roblox Bridge to Creator Hub, REST API
  + SDKs + MCP server + bulk generation (50+ concurrent).
- Why: custom tycoon art (bots, buildings) without an artist. Note: Meshy 6
  downloads need a paid plan; free tier is CC BY 4.0.
- Sources: https://github.com/meshy-dev/Meshy-guide , https://www.meshy.ai/use-cases/free-game-assets/roblox-developers

## Recommendation (shortlist)

**Adopt now:** Fusion (UI) + Wally (installer) + Selene/StyLua (gates) +
Rokit (pinning) + TestEZ/Lune (verification). This is the concrete answer to
"how do we get better at building": better UI quality, enforced code quality,
reproducible toolchain, automated checks — all feeding the one-shot loop.

**Later:** Argon (two-way sync), Tarmac + Blender/Meshy (custom art).
