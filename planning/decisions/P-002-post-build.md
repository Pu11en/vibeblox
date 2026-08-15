# P-002 — What happens after a repo is built?

**Status:** complete (Drew, 2026-08-15)
**Depends on:** P-001

## Confirmed decision

**Repo link only, for now.** Finished projects end with the real GitHub
repo link. Deployment to a host (Railway/Render/Glitch) gets added when we
start building web-app ideas that need to run online — the flow then asks
"does this need to run online?" and deploys just those.

## Completion check

cli.py ends with the repo URL and no deploy step — confirmed.
