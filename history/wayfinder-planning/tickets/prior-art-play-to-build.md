# Does anything like this already exist?

> `wayfinder:research` — child ticket of the map. Created 2026-08-02. **CLOSED 2026-08-02.**

## Resolution

Full findings: [`planning/research/prior-art-play-to-build.md`](../research/prior-art-play-to-build.md)

- **The specific combination is genuinely novel** — no shipped prior art found for a
  consumer Roblox game whose core loop orchestrates a real external agent backend and
  delivers a real, player-owned artifact (GitHub repo). The idea's ingredients are each
  proven, but never combined on Roblox.
- Closest near-miss: **Tycono** — started as exactly this ("AI office tycoon game" where
  agents write real code) but stripped the game and shipped a dev CLI. It validates the
  underlying engine concept, not the game.
- "Play IS real work" is proven at massive scale (Foldit, EVE Project Discovery, ESP Game).
- **The policy wall is the biggest open design question:** Roblox ToS strips Robux of
  real-world value; artifacts delivered into the *player's own* external accounts is a
  different lane than selling value in-game, but needs design care (and never sell the
  artifact itself for Robux).
- Borrowables: Foldit-style automated real-quality scoring (CI-green as the game's quality
  bar), Project Discovery's narrative framing, PLS DONATE's escalation spectacle, Tycono's
  org-tree dispatch as the tycoon hire/upgrade loop.
- Lesson from the badge literature: gamification sticks only when tied to real verified
  artifacts, not badges.

## Question

Scan for prior art on "playing a game IS doing real work with AI" — specifically:

1. **Roblox experiences wired to real external work** — games that call live third-party
   APIs/backends (not look-alikes), games that push real output somewhere (GitHub, real
   accounts), experiences monetizing external compute via Robux.
2. **Games that gamify real coding/AI work** — "you play, code gets written" projects:
   tycoon/management-game skins over actual agent runs, "play-to-build" tools, VS Code/IDE
   gamification, GitHub-driven games.
3. **AI-agent game layers** — any known attempt to wrap agentic coding (Wayfinder-style
   planning/execution) in gameplay for non-programmers or for fun.

Deliverable: a findings list with links, what exists vs. what's genuinely novel in Drew's
idea, and anything worth borrowing (mechanics, UX, monetization patterns).

Context: shapes the map's destination and ticket 3 (play loop). Findings land in
`planning/research/` (no git repo here — no branch).
