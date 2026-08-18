# GITBUTT map

label: wayfinder:map
tracker: local markdown
Status: complete (2026-07-31) — all six tickets closed; decisions locked; the build follows as its own effort. Amended 2026-08-14: the build pivoted from a scheduled dashboard to a natural-language ZCode plugin (see Amendment below).

## Destination

A working local dashboard, running on Drew's machine, where @GithubAwesome channel repos become money-ranked product ideas:

- Page 1: endless feed of every repo from the channel, each with an AI summary (what it is, who it's for).
- Page 2: live idea board. DeepSeek V4 Flash glues one or two repos into a product idea. A research agent scores every idea on how likely it is to make money via email marketing and outreach. High scorers become idea cards: pitch, repos used, score with evidence, ready-to-send outreach email draft.
- A daily scraper pulls each new channel video into the repo database.

The map ends when every decision needed to build this is resolved. The build follows as its own effort.

## Notes

- Tracker: local markdown (no issue tracker provided). Convention: this file is the map; tickets live in `tickets/<slug>.md`, each with a header (Title, Status, Type, HITL, Blocked by, Assigned) and a `## Question` body; closing a ticket sets Status: closed and appends `## Resolution`; research findings go in `research/<name>.md` and are linked from their ticket; claim a ticket by filling Assigned before any work.
- Domain: local web dashboard (Python + SQLite), scheduled DeepSeek V4 Flash agents, daily YouTube scrape. Sibling to the channel-brains MCP package: reads its SQLite database read-only, never modifies it.
- Skills to consult: wayfinder, hermes-agent (cron jobs, config), youtube-content.
- Drew's standing preferences: short plain English, zero em dashes, one question at a time with a recommendation, zero-touch automation (schedule everything, nothing to remember), Proceed = execute.
- Execution follows charting: when the frontier clears, the build happens as separate sessions.

## Decisions so far

- Destination: working local dashboard with live agents (2026-07-31, charting).
- Idea card output: high-scoring ideas carry pitch, repos used, money-odds score with evidence, and a ready-to-send outreach email draft (2026-07-31, charting).
- Research the money signals sources — free keyless sources verified: GitHub REST (60/hr core, 10/min search), HN Algolia, npm, crates.io, PyPI, YouTube RSS, Substack archive, pullpush Reddit archive (frozen May 2025); Reddit JSON (403), Google Trends (429), DuckDuckGo (0) blocked; 9-signal Tier 1/2/3 scoring list proposed; GitHub PAT recommended before building the ranker (2026-07-31).
- Prototype the repo extraction pipeline — video descriptions carry exact GitHub URLs; regex extraction validated on all 50 videos, counts matched titles; backfill approved and done: 1217 distinct repos in data/repos.sqlite3; new videos detected via channel RSS (2026-07-31).
- Name the money-odds rubric — score 0-100: demand proof 30, email reachability 25, competitive gap 15, ship ease 15, product potential 15; kill switches: archived = 0, AGPL warning, no README cap 40; Tier 1 signals per idea, Tier 2 for top 20 (2026-07-31).
- Choose the agent architecture — one local Python service, three DeepSeek V4 Flash jobs (scrape daily, generate twice daily, rank after each run), triggered by Hermes cron; DeepSeek key read from the service .env (2026-07-31).
- Design the dashboard — FastAPI + SQLite + vanilla HTML/JS, port 4325 (4324 was occupied); page 1 endless repo feed with AI summaries, page 2 idea board with score breakdowns and copy-ready outreach emails; new tables in repos.sqlite3 (2026-07-31).
- Set the idea generation rules — single repos always allowed; two-repo combos only with stated fit; 10 ideas max per run; dedupe by repo set; repos used 5+ times deprioritized; top 20 re-score weekly (2026-07-31).
- Build increment: dashboard server live on port 4325 (feed, idea board with score breakdowns and copy-ready emails); summarize / generate / rank / scrape agents implemented as `uv run repo-idea-lab <cmd>`; two cron jobs scheduled: daily scrape (12:00) and pipeline summarize+generate+rank (07:00, 19:00), scripts in hermes scripts dir (2026-07-31).

## Amendment (2026-08-14): GITBUTT plugin

The destination changed, approved by Drew after planning questions:

- The project is now **GITBUTT**, a ZCode plugin driven by natural language
  in a session. No cron jobs, no Hermes, nothing automatic.
- Dashboard deleted. The plugin ships a skill and an MCP server with tools:
  status, scrape_new, summarize_missing, search_repos, build_ideas,
  landscape, spotlight, digest, top_ideas, rank_ideas.
- Channel-brains dependency dropped; summaries use video descriptions and
  README excerpts. Existing transcript-derived summaries stay as data.
- Money scoring (rank, tier2, email drafts) kept, on demand only.
- Folder renamed to `/home/drewp/main-projects/GITBUTT`; duplicate Windows
  copy and `jobs/` deleted.

## Not yet specified

- Idea lifecycle: re-ranking cadence, retiring stale ideas, freshness of the board as repos accumulate.
- Historical videos older than the brain's 50 are not backfilled; the daily RSS scrape covers new videos going forward. Decide later whether older history matters.
- Ranking triggers: re-score when new repos land, or only when new ideas appear?

## Out of scope

- Public productization of the dashboard; the destination is local. A public site is a separate effort.
- Any change to the channel-brains package; the dashboard only reads its database.
- Building or shipping the products the ideas describe; this map only finds and ranks them.
- @GithubAwesome video production and anything reusing video footage.
