# P-003 — The idea box: where do ideas come from and how are they chosen?

**Status:** current (planning)
**Depends on:** P-001, P-002

## Decision

How idea cards arrive in the loop (CLI + future Roblox game) and who
chooses them. Feeds execution ticket E-004 (idea feed from the
repo-idealab channel — Drew confirmed 2026-08-15 that we DO want this).

## Context

- Today: 12 built-in kid-friendly cards + "type your own" + surprise me.
- repo-idealab channel posts GitHub repos daily; Drew wants the game to
  become that channel's front end — "there's always ideas coming."
- Research (2026-08-15, codejunkie99/graph-engineering): a knowledge-graph
  approach (entities + relationships + provenance) could organize the repo
  feed into ideas. Concepts only — the package itself is Claude material
  and is NOT installed (standing preference: no Claude configs).
- Standing quality bar: "good repos, not junk" — the idea box should steer
  toward quality.

## Viable options

- A. **Agent-curated feed** — I review the channel's repos (when asked or
  weekly) and turn the good ones into new kid-friendly idea cards; the
  built-ins + custom ideas stay. Quality first, effort per batch.
- B. **Fully automatic feed** — every channel repo becomes an idea card
  automatically. Always fresh, zero curation, quality varies.
- C. **Hybrid** — automatic feed plus a curated "channel picks" section.

## Recommendation

TBD after Drew's answer.

## Completion check

P-003 confirmed; E-004 updated with the chosen feed behavior.
