# E-004 — Idea phase (gitbutt is the engine)

**Status:** complete (2026-08-15)
**Depends on:** P-003

## Outcome

The idea engine is now IN-project: `ideafinder/` (adapted copy of the
GITBUTT engine; package name kept; original stays as the MCP plugin).
Idea sources in order: gitbutt MCP tools -> ideafinder CLI (`uv run
gitbutt scrape|summarize|generate|rank`) -> `backend/idea_finder.py`
(read-only fallback). Proven end-to-end: gitbutt's top idea (Local
Grammar Assistant, 87.6) built -> real repo (11s, $0.0004).

## Next eligible

E-006 — Simulation & blueprint layer (diagram-design skill; hub + workspace
visuals) — in progress.
