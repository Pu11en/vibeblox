# What can a Roblox game integrate with externally?

> `wayfinder:research` — child ticket of the map. Created 2026-08-02. **CLOSED 2026-08-02.**

## Resolution

Full findings: [`planning/research/roblox-external-integration-capabilities.md`](../research/roblox-external-integration-capabilities.md)

- **The private validation loop is fully supported by official Roblox mechanics.**
  - Game → backend: `HttpService` from server scripts — HTTPS public domains, 500
    external req/min per server, "Allow HTTP Requests" toggle, credentials via the
    game's Secrets store (server-only). Tunnels (ngrok/Cloudflare with a real domain)
    are the portable path for a personal backend; localhost works for Studio plugins,
    RFC1918 from published servers is community-consensus-blocked (uncertain).
  - Backend → agents: no constraint; backend runs whatever engine we choose.
  - Backend → GitHub: no official Roblox↔GitHub integration exists, but the backend
    calls GitHub's REST API directly with its own credentials (GitHub App token or PAT) —
    trivial and standard.
  - Backend → game (progress back): Open Cloud `publishMessage` (≤1 KiB, near-real-time)
    → `MessagingService:SubscribeAsync`, or Data Store API (≤4 MB) + polling.
  - Monetization plumbing for the North Star exists too: DevProducts →
    `ProcessReceipt` (idempotent via `UpdateAsync`); cross-game dev-product sales
    disabled 2026-05-30.
- **Policy: no rule prohibits "game drives external agents."** Constraints are about
  content (AI disclosures, Restricted/18+ label for extended AI chats) and commerce
  (Robux-only, off-platform URLs only via Social Links). AI content is allowed with
  disclosure.
- Design rules that follow: everything server-side; HMAC-sign requests to the backend
  (anti-replay); push results via Open Cloud rather than polling; never trust the client
  with credit balances; private loop needs no user auth (backend's own GitHub token).
- Six uncertainty flags in the file (private-IP blocking, plain HTTP, body-size limits,
  Luau Execution API purpose, tunnel allowance, PAT endpoint quirks) — the private-IP one
  is the only one that matters for us, and the tunnel avoids it entirely.

## Question

Enumerate the external-integration capabilities and hard limits of a Roblox experience
(2026), and give a verdict on the legal bridge for our loop:

1. **HttpService** — current rules: HTTPS-only? allowlisted domains? Are localhost/private-IP
   (RFC1918) calls blocked from Studio and/or from a published place? How does one reach a
   personal backend for private testing (ngrok/Cloudflare tunnel with custom domain?)?
2. **Open Cloud API** — what can it do from outside Roblox (places, assets, datastores,
   messaging), and does it help the loop (e.g., a backend writing to the game)?
3. **GitHub integration** — can a Roblox experience authenticate a user to GitHub (OAuth flow
   via a custom backend with client secret?), and what are the limits on pushing repos/code?
4. **Monetization plumbing for the future North Star** — DevProducts / Marketplace API:
   how purchases are made and verified server-side (to later sell "API credits").
5. **ToS / policy limits** — streaming externally-generated (AI) content into a game, calling
   third-party APIs from the client, any rules that would kill "game drives external agents".

Deliverable: a capability table (mechanism, works from Studio?, works when published?,
cost/auth notes) plus a recommended bridge shape for the private validation loop.

Context: this is the load-bearing feasibility question for the map. Findings land in
`planning/research/` (no git repo here — no branch).
