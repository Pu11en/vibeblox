Title: Name the money-odds rubric
Status: closed
Type: grilling
HITL: yes
Blocked by: none
Assigned:

## Question

What makes Drew look at a repo-based product idea and say "this could actually make money with email marketing"?

Resolve the scoring rubric: dimensions (clear customer type, proven demand, existing competitors, realistic price point, email-list reachability, effort to ship) and rough weights. Grill one question at a time, with concrete examples from his own marketing experience. Offer a default rubric he can edit; the rubric becomes the ranking agent's scoring spec. Feed from the money signals sources research.

## Resolution (approved by Drew 2026-07-31)

Money-odds score 0-100, six weighted dimensions. Every point is backed by a stored evidence excerpt from a verified source.

- Demand proof (30 points): stars, package downloads (npm / crates / PyPI), HN mentions. Proof people already use or want this.
- Email reachability (25 points): niche community volume (subreddits via pullpush) plus newsletters already covering the niche (Substack archives). Can we find 100+ people with this problem who read email?
- Competitive gap (15 points): niche size (GitHub search) vs known competitors, and a realistic price point from pricing pages. Crowded is hard, empty is risky, a real gap is good.
- Ship ease (15 points): repo health: README present, permissive license, pushed within 90 days, star count. Can an engineer clone it and ship an MVP this week?
- Product potential (15 points): standalone product shape (UI, API, or server, homepage exists) and YouTube review coverage. A bare library scores low.
- Kill switches: archived repo = score 0; AGPL = hard warning; no README = capped at 40.

Cost: Tier 1 signals (5 HTTP calls) compute demand, ship ease, product potential for every idea; Tier 2 (3-8 calls) computes reachability and gap for the top 20 shortlist only.
