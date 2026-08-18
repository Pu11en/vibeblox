# Wayfinder Map: Play-to-Build — Roblox Tycoon Driving Real AI Work

> `wayfinder:map` — the canonical artifact. Tickets are child files in `tickets/`.
> Created 2026-08-02. Charts the feasibility of a Roblox game where playing IS building.

## Destination

**A working private loop: Drew plays a Roblox tycoon game, the game drives a real agent
backend over HTTP, and completing a "project" produces a real (small, throwaway) repo on
Drew's GitHub. Validated when the loop works end-to-end — a real repo appears — and playing
feels like play, not work.**

The public game (other players, Robux→API credits, GitHub-connect) is the North Star and
deliberately **out of scope** here — but nothing in this validation may foreclose it. The
load-bearing unknown is the same in both: *can a Roblox game be the front end that drives
real agent work landing on GitHub?* This map resolves that, privately and cheaply, with
test projects instead of real ones.

## Notes

- Domain: Roblox game front-end + external agent backend + GitHub delivery. Feasibility-focused
  validation, not game-dev craft — this map produces decisions, then hands the build off.
- Tracker: **local markdown** (no tracker configured in this repo). Tickets are child files in
  `tickets/`; the frontier is this map's open, unblocked, unclaimed children in map order.
- Skills to consult: `/research` subagents for research tickets; `/grilling` + `/domain-modeling`
  for HITL tickets; `/prototype` for the prototype ticket.
- Drew's existing infra (reuse, do not re-probe):
  - `~/main-projects/cinco-h-ranch/scripts/blotato-bridge.py` — API bridge to z.ai GLM-5.2 with
    ~12,270 credits remaining; `thinking:{type:disabled}` needed for clean JSON. A proven pattern
    for "agent API behind an HTTP bridge."
  - Drew runs local coding agents (Codex-style) that make projects in `~/main-projects/`.
  - Roblox Studio lives on the Windows host; WSL cannot run Studio (see `../RESEARCH.md`).
- Standing preferences (Drew, 2026-08-02):
  - Private validation first; public game later as a separate effort.
  - Validation uses **test projects** (throwaway repos), not Drew's real workflow.
  - "Feels like play, not work" is a hard requirement, not a nicety.
  - **Voice-first interaction** — Drew talks naturally to the game; no typing/text where
    possible. The game must understand plain spoken requests.
  - **"Caveman skill" voice everywhere** — the interaction language is deliberately
    dumbed-down/plain (the technical Wayfinder questioning style is too technical); apply
    this plain-language style across the whole game UX. (The caveman skill itself is not
    installed in this environment as of 2026-08-02 — it's a required design voice; Drew
    can supply it.)
  - **Open-ended building** — the loop must be able to create *anything* Drew asks for,
    and produce **good** repos, not templates or junk. "Build anything you want" is the bar.
  - **MVP first, then v1/v2/v3** — the MVP is a deliberately minimal loop; refinement
    happens by *playing it* and improving, iteratively.
  - Engine: DeepSeek V4 Flash; generous credit posture (see Decisions so far).
- Background docs for the *future* public-game effort (not this map): `../RESEARCH.md`
  (toolchain/workflow), `../MATERIALS.md` (materials/assets).

## Decisions so far

<!-- the index — one line per closed ticket: enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [Which agent engine powers the backend?](tickets/agent-engine-and-cost.md) — **DeepSeek
  V4 Flash via API**, pay-as-you-go, credits top-up-able on demand; **generous credit
  posture** (the future business model IS selling credits to players — generosity now also
  validates the product shape); no stub phase; backend must track per-run cost as future
  pricing input.
- [What can a Roblox game integrate with externally?](tickets/roblox-external-integration-capabilities.md) — **the loop is possible**: server-side HttpService (HTTPS, 500 req/min, Secrets store) + tunnel/VPS backend + GitHub REST push + Open Cloud `publishMessage` back into the game; no policy rule blocks "game drives external agents" (AI disclosure rules apply). Findings: `planning/research/roblox-external-integration-capabilities.md`.
- [Does anything like this already exist?](tickets/prior-art-play-to-build.md) — the
  combination (Roblox tycoon → real agent backend → player-owned GitHub repo) has **no
  shipped prior art**; closest is Tycono (pivoted to a dev CLI). "Play IS real work" is
  proven at scale (Foldit, Project Discovery). Biggest open risk: Roblox ToS policy around
  artifacts with real-world value. Findings: `planning/research/prior-art-play-to-build.md`.
- [How should the tycoon play loop feel?](tickets/tycoon-play-loop-feel.md) — **clicking,
  not typing**: idea cards → three A/B/C questions → build → repo + cash. Caveman-simple
  copy everywhere; TTS reads progress aloud. Voice-input (STT) deferred — no official
  Roblox path yet.
- [What is the game → backend → GitHub bridge architecture?](tickets/bridge-architecture.md) — **built as v0.1**: local WSL stdlib Python backend (reachable from Studio as `http://127.0.0.1:8000`, Cloudflare tunnel for published), shared-secret header, game polls `/api/status` every 4s, DeepSeek `deepseek-v4-flash` agent ($0.14/$0.28 per 1M), syntax check + one auto-fix, GitHub classic PAT pushes public `play2build-*` repos. Per-run cost tracked.
- [What counts as "it works"?](tickets/validation-bar.md) — **one live playthrough** (click → answers → workers → real public repo on GitHub) plus Drew's "felt like play" vibe check; second round with a different idea to prove it's not a fluke; ~2-3 min patience budget for small projects.
- *Premise (2026-08-02, no ticket): the destination is a private validation loop with test
  projects; the public game is North Star, out of scope; "playing = building" means real agent
  work lands as a real GitHub repo.*
- **v0.1 build exists** (`play2build/`): backend + game compiled to
  `game/build/play2build.rbxlx`, code-tested with mock engine; pending Drew's keys
  (DeepSeek + GitHub token) and a live playthrough.

## Frontier (open, unblocked tickets)

1. ~~[What can a Roblox game integrate with externally?](tickets/roblox-external-integration-capabilities.md)~~ — **closed**; see Decisions so far.
2. ~~[Does anything like this already exist?](tickets/prior-art-play-to-build.md)~~ — **closed**; see Decisions so far.
3. ~~[How should the tycoon play loop feel?](tickets/tycoon-play-loop-feel.md)~~ — **closed**; see Decisions so far.
4. ~~[Which agent engine powers the backend?](tickets/agent-engine-and-cost.md)~~ — **closed**; see Decisions so far.
5. ~~[What is the game → backend → GitHub bridge architecture?](tickets/bridge-architecture.md)~~ — **closed**; see Decisions so far.
6. ~~[What counts as "it works"?](tickets/validation-bar.md)~~ — **closed**; see Decisions so far.

No open tickets remain. The map's next move is not a decision ticket but the
**live playthrough** of the v0.1 build (validation bar), then iterating by
playing (v1/v2/v3).

## Not yet specified

- **Repo-idealab idea feed** — pulling daily ideas from Drew's YouTube
  channel into the game. The seam exists (`/api/ideas`); the static list in
  `backend/ideas.py` is the placeholder. Deferred to v1.
- **Speech-to-text input** — talking TO the game (the v0.1 loop is
  click-only + TTS reading back). Roblox has no official STT; needs
  research. Deferred to v1.
- **"Good repos" hardening** — v0.1 approximates CI with local syntax
  checks + a quality-bar prompt; real acceptance gates (run the project,
  test it) are a v1 item.
- **The public game** — other players, Robux→API-credit economy, GitHub
  OAuth for strangers, moderation, marketing, launch. North Star only;
  returns as a fresh effort.

## Out of scope

- **The public game itself** — other players, Robux→API-credit economy, GitHub OAuth for
  strangers, moderation, marketing, launch. North Star only; returns as a fresh effort.
- **Drew's real workflow through the game** — the destination is test projects; real projects
  return only if the destination is redrawn.
- **Game-dev craft** (materials, toolchain, map building — `../RESEARCH.md`, `../MATERIALS.md`):
  relevant to the public-game follow-on, not to this validation.
