# NEXT SESSION: GITBUTT plugin handoff (2026-08-14)

Read this first, then `README.md` and `wayfinder/map.md` for decisions.

## What changed (2026-08-14)

- Renamed from Repo Idea Lab to **GITBUTT**. Folder:
  `/home/drewp/main-projects/GITBUTT`, package `gitbutt`, CLI `gitbutt`.
  Not a git repo; the rename was a plain filesystem move.
- Rebuilt as a **ZCode plugin**: `.zcode-plugin/plugin.json` (skill + MCP
  server), registered in `~/.zcode/cli/config.json` `plugins.dirs`
  (identity `gitbutt@inline`). The skill and MCP tools load in new sessions.
- **No automation**: cron jobs and Hermes scripts removed. Everything runs on
  demand in a session: `scrape_new`, `summarize_missing`, `build_ideas`,
  `rank_ideas` via MCP tools, or the CLI fallback.
- Dashboard (FastAPI + static pages, port 4325) deleted.
- Channel-brains dependency dropped: `transcripts.py` and the `transcribe`
  command removed; scrape no longer syncs captions. Summaries now use
  video descriptions + README excerpts. Existing transcript-derived
  summaries remain in the database as data.
- Duplicate Windows copy at `/mnt/c/Users/drewp/main-projects/repo-idea-lab`
  deleted; `jobs/` deleted; `dist/` rebuilt as `gitbutt-0.1.0`.
- Dependencies trimmed: removed fastapi, uvicorn, openai,
  youtube-transcript-api; added `mcp` (MCP Python SDK).

## Where things stand

- Data: `data/repos.sqlite3` (65 videos, 1,391 repos, 1,391 summaries, 30
  ideas, all scored Tier 1 + Tier 2), `data/taxonomy.json` (18 categories).
- MCP server: `src/gitbutt/mcp.py`, 10 tools (status, scrape_new,
  summarize_missing, search_repos, build_ideas, landscape, spotlight,
  digest, top_ideas, rank_ideas). Smoke-tested over stdio.
- Skill: `skills/gitbutt/SKILL.md` teaches agents the tools, the
  "find repos for my current project" flow, and the safety rules.
- DeepSeek key: project `.env` (never print, share, or commit).
- `uv run gitbutt scrape|summarize|generate|rank|tier2|wiki` works.

## Known limitations

- `build_ideas` takes a theme now (`generate(theme=...)`); not yet exercised
  live with a theme.
- 273 repos were unclassified before the taxonomy pass; re-run `gitbutt wiki`
  after new summaries land.
- Tier 2 reachability saturates for broad keywords (pullpush caps at 100
  hits); the newsletter half is the discriminator. Tier 3 (Reddit subscriber
  counts, Google Trends) was designed but never built.
- The old `prototype/extract_repos.py` still references the channel-brains
  database path; it is kept as historical reference only.

## Notes for working in this project

- DeepSeek V4 Flash is a reasoning model: it over-thinks big open-ended
  prompts and returns empty content. Keep prompts small and structured;
  prefer deterministic data-driven logic (tags, co-occurrence) over model
  judgment where possible.
- SQLite lock discipline: never hold a connection open across network calls;
  write in short bursts.
- Always prefix `uv run` with `env -u PYTHONPATH` in this shell (Hermes
  PYTHONPATH pollution).
- `uv sync --extra dev` after pyproject changes to keep ruff/pytest installed.
