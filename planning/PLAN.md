# Plan: Play2Build — harness-first loop, gamified later

**Status:** awaiting approval

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

- In: the loop (CLI + skill + factory), ideas, quality, later: deploy,
  feed, gamified shell.
- Out: the published-place infrastructure saga (separate P1), and the
  Wayfinder planning folder (closed, separate).

## Map

`2/2 planning tickets`

- ✓ [P-001 — Destination](decisions/P-001-destination.md) — depends on: none
- ✓ [P-002 — Post-build](decisions/P-002-post-build.md) — depends on: P-001

## Confirmed decisions

- [P-001](decisions/P-001-destination.md): harness-first — loop as CLI +
  skill, produce real results, gamify into Roblox later.
- [P-002](decisions/P-002-post-build.md): repo link only for now;
  deployment added when web-app ideas appear.

## Execution

- ✓ [E-001 — Harness loop (CLI)](execution/E-001-harness-loop.md)
- ✓ [E-002 — Skill (harness plugin)](execution/E-002-skill.md)
- ○ [E-003 — Deploy web ideas](execution/E-003-deploy-web-ideas.md) — deferred
- ○ [E-004 — Idea feed (repo-idealab)](execution/E-004-idea-feed.md) — deferred
- ○ [E-005 — Gamified shell (Roblox)](execution/E-005-gamified-shell.md) — deferred

## Approval

- Visual review: ready
- Build handoff: not authorized

## Now

- Current: human final review of the plan
- Next: on approval — use the loop (E-001/E-002 are done; iterate with real
  use, then E-003+ in order)
