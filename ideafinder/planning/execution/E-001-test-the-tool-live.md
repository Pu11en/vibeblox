# E-001 — Test the tool live

- Outcome: the themed idea path runs once, end to end, and the read-only
  tools work in a session.
- Depends on: P-001

## Context

- P-001 chose "test and finish". The theme path of `build_ideas`
  (`generate(theme=...)`) was refactored but never run live.
- GITBUTT skill guide: `skills/gitbutt/SKILL.md`.

## In scope

- Run one themed `build_ideas` (theme chosen from the catalog, e.g.
  "self-hosting").
- Demo the read-only tools (search_repos, digest, top_ideas) in-session.
- Run the standard verification: `env -u PYTHONPATH uv run ruff check src/`
  and `uv build`.

## Out of scope

- Fixing bugs beyond reporting them; running `rank_ideas` or `scrape_new`;
  more than one idea run.

## Constraints

- No `.env` contents printed or shared.
- `data/repos.sqlite3` preserved; short SQLite connections.
- One generation run only, to limit quota.

## Proof

- `build_ideas` returns at least one pitched idea.
- Read-only tools return results.
- Ruff passes; build succeeds.

## If blocked or disproven

- If the themed run fails or returns empty, report the exact error. A code
  fix beyond a trivial one returns this to planning.

## Human review

- Drew reads the generated idea and confirms it looks like a real product
  pitch.

## Next eligible ticket

- E-002
