Title: Choose the agent architecture
Status: closed
Type: grilling
HITL: yes
Blocked by: none
Assigned:

## Question

How do the three agents run and on what schedule?

Options: (a) Hermes cron jobs on DeepSeek V4 Flash, agentic with web tools; (b) a scheduler inside the dashboard backend calling the DeepSeek API directly; (c) hybrid: Python pipeline for scrape, summarize, and idea generation (mechanical, cheap, logged in the DB), Hermes cron for the ranking research pass (needs web tooling). Recommendation: (c).

Resolve schedules too: daily scrape, idea run cadence, ranking pass cadence.

## Resolution (approved by Drew 2026-07-31)

One local Python service (the dashboard app) with three DeepSeek V4 Flash jobs, triggered by Hermes cron jobs:

- scrape (daily): channel RSS poll, new video, description, repos into the DB. The prototype script promoted into the app.
- generate (twice daily): DeepSeek V4 Flash creates up to 10 new ideas from the eligible repo pool, stores pitch and repos used.
- rank (after each generate): Tier 1 signals computed per new idea via the verified APIs (plain HTTP, only a free GitHub PAT recommended), then DeepSeek V4 Flash writes the evidence and score narrative. Tier 2 signals for the top 20.

Why: every verified signal source is plain HTTP, so no browser-based web tooling is needed (Hermes web tools are not configured on this machine anyway). Direct DeepSeek API calls are cheap and logged in the DB. Hermes cron gives zero-touch scheduling and visibility. The service reads the DeepSeek API key from its own .env.
