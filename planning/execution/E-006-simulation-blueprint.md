# E-006 — Simulation & blueprint layer (session UX)

**Status:** in progress
**Depends on:** E-002 (skill), diagram-design skill (installed)

## Outcome

When Drew "pretends to play" in the session: the plugin narrates the game
scene in detail (hub, workspace, workers, vault — what the player sees at
this moment), treats his inputs as in-game inputs, and renders the world as
visuals:

- HTML blueprints via the `diagram-design` skill (bird's-eye view of the
  hub + a player's workspace; backend process flow; the plan in progress).
- Rich written narration as fallback ("an AI writing it all out").
- Each input/output pair mirrors what the real game would show.

## Next eligible

E-005 (gamified shell) — the design is exercised here first.
