# P-001 — Destination: what game are we building?

**Status:** complete (confirmed by Drew, 2026-08-15)
**Depends on:** none

## Confirmed decision

**Harness-first.** Build the Play2Build loop as a tool that runs inside the
harness/session (a CLI + later a plugin the harness uses): pick an idea →
answer A/B/C questions → precise plan → real repo gets built → deploy →
link. Produce real results first; wrap it as a plugin; THEN make it gamified
into the Roblox game as the final shell. The game-dev craft is not the
bottleneck — the loop is — so the loop gets built and used first.

Drew's words: "we can build the entire thing in the harness and then... as a
plugin right that harness uses and then like once we do a lot of work with
it and like we start producing real results then we can make it gamified."

## Effect on the plan

- The current v0.1 Roblox game + factory stays as-is (it's the gamified
  shell prototype AND the real engine).
- The next build is the harness loop: `backend/cli.py` (idea cards →
  A/B/C questions → job → repo URL), same backend, same engine.
- Deployment (Railway or similar) and the plugin packaging are follow-up
  tickets.

## Completion check

Destination is one sentence in PLAN.md — done. Route: harness loop first,
gamified shell later — done.
