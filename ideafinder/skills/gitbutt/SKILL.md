---
name: gitbutt
description: GITBUTT turns repositories featured by the @GithubAwesome YouTube channel into product ideas, driven by natural language in a session. Use when Drew asks to check gitbutt, find repos that help a current project, scrape the most recent channel videos, make something from the repo knowledge, browse or digest repos, or score ideas for money potential.
---

# GITBUTT

A local ZCode plugin holding a database of every repository the @GithubAwesome
channel features, plus the summaries, categories, ideas, and scores derived
from them. Nothing runs automatically: every scrape, summary, idea, and
ranking happens when Drew asks for it in a session.

The plugin exposes MCP tools (names below) and a manual CLI. The database
lives at `/home/drewp/main-projects/GITBUTT/data/repos.sqlite3` and the
taxonomy at `data/taxonomy.json`.

## Tools

| Tool | When to use |
|---|---|
| `status` | First call when in doubt: counts, missing summaries, last scrape. Read-only. |
| `scrape_new` | "Get the most recent videos / new repos". Fetches new @GithubAwesome videos from the channel RSS and extracts their repos. Hits the network and mutates the DB. |
| `summarize_missing` | After a scrape: summarize repos that have no summary yet (DeepSeek + README excerpts). Mutates the DB. |
| `search_repos` | "Find repos that help my project X". Free-text search over names, tags, summaries, and categories. Read-only. |
| `build_ideas` | "Make something / give me N ideas about X". One or two repos glued into a pitched product concept, optionally themed. Mutates the DB. |
| `landscape` | "What's the landscape of X". Category definitions, related categories, repo counts; falls back to a repo search when the topic matches no category. Read-only. |
| `spotlight` | Deep dive on one repo: summary, tags, category, the video it first appeared in, ideas it is used in. Read-only. |
| `digest` | "What's new". The most recently added repos, newest first. Read-only. |
| `top_ideas` | "What ideas do we have". The idea board with scores and email drafts, best first. Read-only. |
| `rank_ideas` | "Score the ideas". Money-odds ranking (Tier 1 signals, email drafts, Tier 2 reachability and pricing). Heavy network use; on demand only. |

## The "find repos for my current project" flow

When Drew is building something and wants repo help: ask what the project is
about, call `search_repos` with the key terms (repeat with synonyms), and
offer the best matches with their summaries. If he wants to go further, call
`build_ideas` with the project as the theme.

## CLI fallback (if MCP tools are unavailable)

```bash
cd /home/drewp/main-projects/GITBUTT
env -u PYTHONPATH uv run gitbutt scrape|summarize|generate|rank|tier2|wiki
```

## Safety rules

- `scrape_new`, `summarize_missing`, `build_ideas`, and `rank_ideas` consume
  network and model quota and mutate the database. Run them only when Drew
  explicitly asks; `status` is the cheap read-only check.
- Never print, share, or commit `.env` (it holds the DeepSeek key).
- Keep SQLite connections short; never hold one open across a network call.
- DeepSeek V4 Flash is a reasoning model: it over-thinks big open-ended
  prompts and returns empty content. Keep prompts small and structured.
- GITBUTT is a local prototype, not a proven business or public product.
- The old channel-brains integration is gone: GITBUTT is standalone and never
  touches the channel-brains database.
