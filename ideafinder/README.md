# ideafinder

The idea engine for Play2Build — a working copy of the GITBUTT engine,
brought into this project and adapted (2026-08-15). The original stays at
`~/main-projects/GITBUTT` (registered as a ZCode plugin with MCP tools);
this copy is the engine we configure and modify for this project.

## What it holds

- `data/repos.sqlite3` — 65 channel videos, 1,391 repos, summaries, 30
  scored ideas with email drafts.
- `data/taxonomy.json` — repo categories.
- `src/gitbutt/` — the Python package (scrape, summarize, generate ideas,
  rank for money potential). Package name kept as `gitbutt`.
- Its own planning/wayfinder docs (from the original — untouched).

## CLI (from this folder)

```bash
uv run gitbutt scrape      # new videos -> new repos (on demand, network)
uv run gitbutt summarize   # summaries for repos missing them (model quota)
uv run gitbutt generate    # new product ideas from the pool (model quota)
uv run gitbutt rank        # money-rank the ideas (network + quota)
```

Nothing runs automatically — every job is on demand.

## Using it in the Play2Build flow

1. Idea phase: `top_ideas`/`build_ideas` via the gitbutt MCP tools (session)
   or the CLI above from this folder.
2. Feed the winning card into the build loop:
   `cd ../backend && python3 cli.py --auto-idea custom --auto-name "<name>" --auto-answers a a b`
3. Repo lands on GitHub (verified before push).

Fallback for the idea phase when neither MCP tools nor this CLI is
available: `backend/idea_finder.py` (read-only DB access).
