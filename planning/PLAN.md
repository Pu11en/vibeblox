# Plan: Play2Build — harness-first loop, gamified later

**Status:** planning

## Continuation

- Mode: manual
- Latest boundary: none
- Successor task: none

## Destination

A usable Play2Build loop that runs in the harness first — pick an idea,
answer A/B/C questions, get a precise plan, receive a real repo. The Roblox
game becomes the gamified shell on top, built only after the loop produces
real results.

## Success

- Drew runs the loop in the harness and gets a real repo from a few A/B/C
  answers — already proven (3 real public repos). The gamified Roblox shell
  is a later phase, not a prerequisite.

## Boundaries

- In: the loop (CLI + skill + factory), ideas (built-in + custom + feed),
  quality, later: gamified shell.
- Out: deployment (E-003 removed by Drew 2026-08-15), the published-place
  infrastructure saga (separate P1), the Wayfinder planning folder (closed,
  separate).

## Map

`2/3 planning tickets`

- ✓ [P-001 — Destination](decisions/P-001-destination.md) — depends on: none
- ✓ [P-002 — Post-build](decisions/P-002-post-build.md) — depends on: P-001
- ▶ [P-003 — The idea box](decisions/P-003-idea-box.md) — depends on: P-001

## Confirmed decisions

- [P-001](decisions/P-001-destination.md): harness-first — loop as CLI +
  skill, produce real results, gamify into Roblox later.
- [P-002](decisions/P-002-post-build.md): repo link only (deployment
  removed from the route, 2026-08-15).
- (P-003 in progress)

## Execution

- ✓ [E-001 — Harness loop (CLI)](execution/E-001-harness-loop.md)
- ✓ [E-002 — Skill (harness plugin)](execution/E-002-skill.md)
- ○ [E-004 — Idea feed (repo-idealab)](execution/E-004-idea-feed.md) — wanted; behavior from P-003
- ○ [E-005 — Gamified shell (Roblox)](execution/E-005-gamified-shell.md) — confirmed wanted

## Approval

- Visual review: not ready (planning continues)
- Build handoff: not authorized

## Now

- Current: P-003 — The idea box: where do ideas come from and how are they chosen?
- Next: settle P-003, then continue deepening the plan
