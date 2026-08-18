Title: Research the money signals sources
Status: closed
Type: research
HITL: no
Blocked by: none
Assigned:

## Question

Which free, automatable data sources can score how likely a repo-based product is to make money via email marketing?

Candidates to verify with a real HTTP call each: GitHub API (stars, topics, description, language), Hacker News Algolia API (mentions), Reddit JSON search (community size, complaints, requests), Substack / newsletter search (letters covering the niche), YouTube search (reviewers), competitor pricing pages via web fetch. Note auth needs, rate limits, and what each signal actually means for email marketing success.

Deliver findings to wayfinder/research/money-signals-sources.md, plus a proposed signal list the ranking agent can compute cheaply.

## Research findings

Linked: [research/money-signals-sources.md](research/money-signals-sources.md) (2026-07-31). Verified with real curl calls: GitHub REST (60/hr core, 10/min search), HN Algolia (no auth), npm, crates.io, PyPI metadata, YouTube oEmbed/RSS/yt-dlp, Substack per-publication archive, pullpush.io Reddit archive (frozen May 2025), Product Hunt feed. Blocked from this machine: Reddit JSON (403), Google Trends (429), DuckDuckGo (0 results), Substack search API (404), pypistats (429). Proposed 9-signal list in Tier 1 (every idea, 5 calls) / Tier 2 (shortlist) / Tier 3 (top 10) buckets.
