# P-001 — Scope of the next round

- Status: complete
- Depends on: none

## Decision

How much of the "next" worklist belongs in this round: test what is built,
finish the catalog, or also build the optional extras. This sets the whole
map, so it comes first.

Context: the plugin is built and working (65 videos, 1,391 repos, 30 ideas,
all scored). One code path (themed idea generation) was never run live, and
273 repos lack a category label. Two extras were designed but never built:
Tier 3 scoring (Reddit subscriber counts, Google Trends) and backfilling
videos older than the first 50.

## Viable options

- A. Test and finish (Recommended). Run the themed idea generation live,
  label the 273 unclassified repos, and stop. Smallest round; leaves extras
  for later.
- B. Test, finish, and build the extras. Same as A plus Tier 3 scoring and
  backfilling old videos. More work and more quota.
- C. Plan only. Write the worklist now, run nothing yet.

## Recommendation

A — Test and finish. Validates the build with the least risk and quota.

## Confirmed decision

A — Test and finish. Drew replied "a" (2026-08-15), resolved against option A.
This round runs the themed idea generation once and labels the 273
unclassified repos, then stops. Extras (Tier 3 scoring, backfilling old
videos) and the lifecycle questions (re-ranking cadence, retiring stale
ideas) are deferred to a later round.

## Delegation

None.

## Evidence

No external evidence needed; facts from NEXT-SESSION.md and live status.

## Effects

- E-001 tests the tool live; E-002 finishes the catalog. Deferred: Tier 3
  scoring, old-video backfill, lifecycle rules.

## Complete when

Scope chosen and recorded; execution tickets E-001 and E-002 match it.
