# GITBUTT agent guide

## Read first

1. `README.md`
2. `NEXT-SESSION.md`
3. `wayfinder/map.md`
4. The specific source file or Wayfinder ticket affected by the task

## Boundaries

- This folder owns the GITBUTT plugin, local database, generated wiki, and
  project planning.
- GITBUTT is standalone. The channel-brains project at
  `/home/drewp/main-projects/channel-brains` is a separate sibling plugin;
  GITBUTT does not read it, and do not modify it as part of GITBUTT work.
- Course positioning belongs in `/home/drewp/main-projects/Drew's AI course`.
- Nothing runs automatically. There are no cron jobs, Hermes scripts, or
  deployed copies to synchronize.

## Safety

- Never print, share, or commit `.env`.
- Preserve `data/repos.sqlite3`; it is the working local dataset.
- Do not run scraping, generation, ranking, or other network/model jobs merely
  to inspect the project. Those jobs consume quotas and mutate the database.
  The MCP `status` tool and the read-only tools (search_repos, landscape,
  spotlight, digest, top_ideas) are the cheap ways to look.
- Keep SQLite connections short and never hold one open across a network call.
- Do not describe the local prototype as a proven business or public product.

## Verification

For source changes, run:

```bash
env -u PYTHONPATH uv run ruff check src/
env -u PYTHONPATH uv build
```

Run focused tests when they exist for the changed behavior. After changes to
`src/gitbutt/mcp.py` or the plugin manifest, smoke-test the MCP server over
stdio (initialize, tools/list, one read-only tool call).

## Version control

This folder was not a Git repository when it was organized on 2026-08-06.
Inspect again before making future changes. Do not initialize, publish, or
commit it without Drew's direction and a review of secrets, private data, and
generated artifacts.
