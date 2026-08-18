# E-004 — Idea phase (gitbutt is the engine)

**Status:** complete (2026-08-15)
**Depends on:** P-003

## Outcome

The idea phase uses gitbutt's own MCP tools (status / digest /
search_repos / build_ideas / top_ideas / rank_ideas) — on demand, nothing
automatic. Proven end-to-end: gitbutt's top idea (Local Grammar Assistant,
score 87.6) built through the loop -> real repo (11s, $0.0004).
`backend/idea_finder.py` is demoted to a fallback (read-only DB access)
for when gitbutt's tools are unavailable; `cli.py --find-idea` remains as
the fallback path.

## Next eligible

E-006 — Simulation & blueprint layer (diagram-design skill; hub + workspace
visuals) — in progress.
