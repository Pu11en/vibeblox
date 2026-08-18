# E-002 — Finish the catalog

- Outcome: every repo has a category label and the wiki is regenerated.
- Depends on: E-001 (route order)

## Context

- 273 repos were unclassified before the taxonomy pass
  (NEXT-SESSION.md); all 1,391 repos now have summaries, so classification
  can complete.

## In scope

- Run `env -u PYTHONPATH uv run gitbutt wiki` to classify the unclassified
  repos and regenerate the wiki pages.

## Out of scope

- Tier 3 scoring, backfilling old videos, new categories, deleting data.

## Constraints

- No `.env` contents printed or shared.
- `data/repos.sqlite3` preserved; taxonomy stays in `data/taxonomy.json`.

## Proof

- `status` shows zero unclassified repos.
- `wiki/` pages regenerated with the new labels.

## If blocked or disproven

- If classification quality is poor or the run fails, report and return to
  planning before forcing labels.

## Human review

- Drew can spot-check one wiki page.

## Next eligible ticket

- Plan complete for this round; deferred items (Tier 3, backfill, lifecycle
  rules) recorded in P-001.
