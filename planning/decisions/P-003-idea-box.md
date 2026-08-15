# P-003 — The idea box: where do ideas come from and how are they chosen?

**Status:** complete (confirmed by Drew, 2026-08-15)
**Depends on:** P-001, P-002

## Confirmed decision

**On-demand Idea Finder, money-scored, not kid-friendly.** The idea source is
the GITBUTT repo pool (the rebranded repo-idealab; DB at
`~/main-projects/GITBUTT/data/repos.sqlite3`). Finding an idea is an explicit
on-demand action (natural language or a short command — nothing automatic).
Each find run scores candidates for **money potential + fastest go-to-market**
with DeepSeek and returns an idea card: pitch, why it makes money, fastest
path, content angle, starting-point repo. The card is the head start: humans
articulate plans better from something real than from nothing. The game can
later gamify grabbing an idea and starting work on it.

Drew's words (2026-08-15): "you review the channel's repos and figure out if
the good ideas will be able to make money... research the best way to go to
market or the fastest way to start making money with it"; "I don't want it to
be fully automatic... it would be on demand"; "no it's not going to be kid
friendly."

## Effect on the map

- E-004 becomes the Idea Finder (built: `backend/idea_finder.py` +
  `cli.py --find-idea`, proven end-to-end with a real repo).
- Quality bar re-affirmed: real products, not quick junk ("10-60 second
  repos" framing rejected — speed is fine, quality is the point).
- Verification/junk-gates: later, not now (Drew: "we'll do that later").

## Completion check

On-demand finder exists, scores for money + go-to-market, feeds the loop —
proven with a live build.
