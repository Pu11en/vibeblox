# Which agent engine powers the backend?

> `wayfinder:grilling` — child ticket of the map. Created 2026-08-02. **CLOSED 2026-08-02.**

## Resolution

Decided by Drew, 2026-08-02:

- **Engine: DeepSeek V4 Flash via API** — cheap pay-as-you-go, and Drew can add credits
  on demand. No LLM-free stub phase; no local-agent route. The loop goes straight to a
  real LLM engine (the stub question is moot — the engine is cheap enough to skip it).
- **Credit posture: generous.** No tight per-run cap. Rationale: the future public game's
  business model IS selling credits to players ("eventually I'll make money from people
  spending money on more credits"), so being generous now is also validating the product
  shape. Backend must still **track per-run cost** — that number becomes the future
  pricing input (and the private validation's cost record).
- The backend's agent loop (single-call repo generation vs. multi-agent pipeline) is not
  decided here — that belongs to the bridge-architecture ticket.

## Question

What actually generates the test-project repos behind the game? Decide among:

1. **Existing z.ai credits** — the proven Blotato-bridge pattern (z.ai GLM-5.2 API, ~12,270
   credits) writing small repos. Known cost behavior, zero new signups.
2. **Local coding agents** — the Codex-style agents Drew already runs, invoked by the
   backend. Real project-quality output; cost in API usage rather than credits.
3. **LLM-free stub first** — a deterministic backend that writes a real (template-based)
   repo without any AI, to prove the game→backend→GitHub loop before spending on models.

Also decide the **cost envelope**: an acceptable per-playthrough credit/budget ceiling for
validation runs.

Context: whatever is chosen becomes a building block of the bridge architecture (ticket 5).
The stub is never the destination — the question is whether validation starts with it or
with a real LLM engine.
