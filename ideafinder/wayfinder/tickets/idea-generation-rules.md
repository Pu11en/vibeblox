Title: Set the idea generation rules
Status: closed
Type: grilling
HITL: yes
Blocked by: none
Assigned:

## Question

What rules govern DeepSeek V4 Flash's idea generation?

Single repo as product, or one-plus-one combos; what makes a combo valid (complementary functions, not two databases); how many new ideas per run; dedupe and novelty (no re-suggesting the same repo pair); which repos are eligible (has a README, looks like a product, not library-only).

Recommendation: single-repo ideas always allowed, combos only when the agent states why they fit, cap N new ideas per run, dedupe by repo set.

## Resolution (approved by Drew 2026-07-31)

- Eligible: every repo in the pool. Kill switches at ranking time handle archived, AGPL, and no-README repos.
- Single-repo ideas always allowed. Combos are exactly two repos, and only when the agent states the fit: "X handles A, Y handles B, together they are a C-for-D product."
- Up to 10 new ideas per run. Dedupe by repo set: a pairing never repeats. Repos already used in 5 or more ideas are deprioritized to keep the board varied.
- Ranking: every new idea gets Tier 1 signals immediately. The top 20 by score get Tier 2. The top 20 re-score weekly for freshness.
