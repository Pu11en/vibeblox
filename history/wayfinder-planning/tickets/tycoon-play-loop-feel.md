# How should the tycoon play loop feel?

> `wayfinder:prototype` — child ticket of the map. Created 2026-08-02.
> **CLOSED 2026-08-14** — answered by Drew + built as v0.1.

## Resolution

Drew's answers (2026-08-14): **clicking, not typing** — lots of A/B/C
selection; a "portable-planner"-style flow: pick an idea → answer a few
plain multiple-choice questions → build. Language must be so simple a
12-13-year-old gets it (caveman voice), while the output stays high-level.
Vibe: Drew had no opinion — went with the classic money tycoon, kept light.

Built as `play2build/game/` (see `play2build/README.md`):

- **Flow:** hub → idea cards (12 kid-friendly, emoji, "🎲 surprise me") →
  3 questions (size / language / fancy, big buttons, one at a time) → build
  screen (progress bar + plain-language stage messages + the plan summary)
  → done (repo URL + cash reward) or failed (retry). No typing anywhere.
- **Tycoon layer:** fake cash from finished projects; hire workers (each =
  one concurrent real build, capped at 3, enforced server-side); Cash
  Machine upgrade (double cash). Session-only economy.
- **Feels:** worker bots hop while working, the vault flashes green on a
  landed repo, TTS reads progress out loud in plain words (mute-able).
- **Language:** all in-game copy is deliberately elementary; the backend
  prompt demands the plan summary be "one or two short, plain sentences a
  10-year-old understands."
- The idea cards and questions live on the backend (`/api/ideas`,
  `/api/questions`) so the game stays dumb — the seam is ready for the
  repo-idealab feed later.
- Voice-input (talking TO the game) is deferred: the hard requirement
  softens to "zero typing, all clicking + listening" for v0.1; STT has no
  official Roblox path yet (see map "Not yet specified").

## Question

What does the player actually DO in-game that maps onto real agent work? The hard
requirement: "feels like play, not work" — playing must not feel like clicking through a
backend admin panel.

Explore via a cheap rough prototype (per the /prototype skill — an outline, mock UI, or
stub logic to react to), then decide:

- The game actions that kick off / steer real work (e.g., place a "server", hire a "worker",
  choose a "quest", spend "focus" tokens) and how they map to backend operations.
- How agent progress is presented (progress bars, notifications, "quest complete" moments)
  without destroying the fantasy.
- The minimal loop that is still fun for one validation playthrough of a test project.

Links the prototype as an asset. Blocked by nothing — but its answer graduates the
"progress presentation" fog into specifics.

### Hard requirements (Drew, 2026-08-02 — add to the map Notes if anything changes)

- **Voice-first:** the player talks naturally to the game; no typing/text where possible.
  The play loop must be speakable — describing what to build out loud is the primary input.
- **Open-ended:** the loop must create *anything* the player asks for — not fixed
  templates — and produce **good** repos (the game's design must steer toward quality,
  not junk).
- **Plain-language voice ("caveman skill" style):** the interaction/questions are
  deliberately dumbed down; nothing like technical grilling language. This voice applies
  to the whole game UX.
- **MVP first:** prototype the smallest loop that can be *played*; refinement comes from
  actually playing it and improving (v1/v2/v3 later).

## Question notes

- Keep it private-validation sized: one player, test projects, no economy.
- The loop shape (game → HTTP → backend → agents → GitHub repo) is assumed; this ticket
  decides the game-side surface, not the plumbing (see the bridge-architecture ticket).
