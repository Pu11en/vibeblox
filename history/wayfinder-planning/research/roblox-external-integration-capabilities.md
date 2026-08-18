# Roblox External Integration Capabilities (2026)

Research ticket: "What can a Roblox experience integrate with externally?"
Researched 2026-08-02 against primary sources: official Roblox documentation (create.roblox.com, docs updated 2026-07-31), Roblox Terms of Use (effective 2026-05-19), Roblox Community Standards, Roblox Creator Third-Party App Policy, GitHub official docs, and Roblox developer-forum announcements by staff. Community-sourced claims are marked `[community]` and flagged as uncertain where no official statement exists.

---

## (a) Capability table

| Mechanism | Works from Studio? | Works when published? | Auth / cost notes |
|---|---|---|---|
| **HttpService → any public HTTPS/HTTP endpoint** | Yes (toggle "Allow HTTP Requests" under File → Experience Settings → Security; not enabled by default) [1] | Yes [1] | No cost. Rate limit: **500 external HTTP requests/min per game server**; Open Cloud calls get a separate **2,500/min per game server**; exceeding stalls ~30 s with "Number of requests exceeded limit" [1][2]. Only ports 80/443 and 1024–65535 except 1194 (blocked ports return 403 / ERR_ACCESS_DENIED) [1][3]. |
| **HttpService → localhost / 127.0.0.1** | Yes — official docs explicitly allow plugins to reach localhost; engine-class docs ship an in-game example calling `http://localhost:11434` (Ollama) [4][5]. Note: `CreateWebStreamClient` (SSE) is **Studio only** [2]. | **No (private RFC1918 addresses unreachable from live servers)** — this is community consensus, not an official documented rule; flag uncertain [community: 6][7]. | No auth; local-only. |
| **HttpService → ngrok / Cloudflare Tunnel with custom domain** | Yes [4] | Yes in principle: tunnels are public HTTPS domains on ports 443/80, which are allowed [1]. No official doc mentions tunnels; community reports of success exist [community: 8]. Do not use free `*.ngrok.io` HTTP URLs (prefer HTTPS). | Public HTTPS required. Backend should require a pre-shared key (official best practice: "Requests should provide a secure form of authentication, such as a pre-shared secret key") [1]. |
| **HttpService → Open Cloud endpoints (in-game)** | Yes (API key stored as a Secret; local secrets in Studio; secrets are only served to live servers / collaborative testing, not local playtesting or client scripts) [9] | Yes [1] | `x-api-key` header must be a Secret from the game's **Secrets store** (≤500 secrets/game, ≤1,024 chars, domain-scoped); only `x-api-key` and `content-type` headers allowed; only HTTPS; `..` forbidden in path params; a defined subset of endpoints (data stores, groups, dev products, game passes, notifications, universes incl. `publishMessage` and `restartServers`, assets, luau execution, etc.) [1]. |
| **Open Cloud REST API from an external backend** (datastores, messaging, places, assets, notifications, etc.) | N/A (backend, not Studio) | Yes — independent of the game's lifecycle [10][11] | Auth via **API key** (`x-api-key` header) or **OAuth 2.0** (authorization code + PKCE, OpenID Connect) [10][12]. Rate limits per API-key owner / per access token; `x-ratelimit-*` response headers; undocumented limits may apply (handle 429) [13]. Free; quota-based. |
| **Backend → writes INTO the game** | — | Yes via three official channels: (1) **Data Store API** — CRUD/increment/versions on data stores, ordered data stores, memory-store queues and sorted maps (`/cloud/v2/...`, API key) that the game reads with `DataStoreService` [14]; (2) **Publish Universe Message** — `POST /cloud/v2/universes/{universe_id}:publishMessage` (Stable) delivers to servers subscribed via `MessagingService:SubscribeAsync` [15][16]; (3) **User notifications** — `POST /cloud/v2/users/{user_id}/notifications` [17]. | API key (data store: API Key only; messaging: API Key/OAuth; notifications: API Key/OAuth/HttpService) [14][15][17]. |
| **Open Cloud Messaging API** | Topic must be created in Studio (via `SubscribeAsync`); API can only reach **live** game servers over HTTP [16]. | Yes [16] | Limits shared with engine MessagingService: **message ≤ 1,024 chars (1 KiB), topic ≤ 80 chars**; publish ≤ `600 + 240 × players`/min per server; receive ≤ `(40 + 80 × servers)`/min per topic, `(400 + 200 × servers)`/min per game; ≤240 subscribe req/min/server [16]. Legacy `/messaging-service/v1/...` endpoint is marked "Not Recommended" — use `publishMessage` [18]. |
| **Open Cloud Data Store API** | N/A | Yes [14] | Entry ≤ **4 MB**; per-key throughput shared with in-game API: reads 25 MB/min, writes 4 MB/min (rounded up per KB); game storage limit `500 MB + 1 MB × lifetime users` [19]. |
| **Open Cloud Places / Assets / Dev-Products / Game-pass APIs** | N/A | Yes (many endpoints Beta) — publish place versions, upload/manage assets, CRUD developer products and game passes from a backend/CI [20][21][22]. | API key / OAuth [20][21][22]. |
| **Luau Execution API (Open Cloud)** | N/A | Endpoints exist (create luau-execution-session-tasks, list logs; Stable) [23]. Purpose/behavior not documented on the reference page — **uncertain**, treat as experimental until a guide exists. | API key [23]. |
| **GitHub integration (official)** | **None.** Roblox has no official GitHub integration for experiences; the full official docs index contains zero GitHub pages [24][25]. Open Cloud does not cover GitHub [10][11]. | — | The real GitHub workflow is third-party dev tooling (Rojo/Azul sync files↔Studio) [26], not a game↔GitHub link. |
| **GitHub OAuth via personal backend** | Feasible — but only with an out-of-game browser: Roblox has no documented in-game browser API (BrowserService exposes no methods) [27]. GitHub supports the **OAuth 2.0 Device Authorization Grant "for apps that don't have access to a web browser"** [28]: show a code in-game, user authorizes at github.com/login/device, backend (which holds the client secret) polls for the token. | Yes [28] | Backend holds GitHub client secret + tokens; never ship to the client. Note Community Standards: displaying external URLs in-game is restricted to the Social Links feature (16+); showing "github.com/login/device" text in-game is a compliance gray area [29]. |
| **Backend → pushes to GitHub repo** | N/A | Yes — backend calls GitHub REST API (git blobs/trees/commits/refs). Git database endpoints are governed by the **Contents** permission for fine-grained PATs, with per-endpoint availability (e.g., `git/refs` ✓, `git/blobs` ✗ for PAT) [30]; GitHub recommends **GitHub Apps** (short-lived installation tokens, fine-grained) over OAuth/PATs for automation [28]. | Free; GitHub rate limits apply. |
| **Monetization — Developer Products** | Purchases in Studio test mode **cost real Robux**; test mode validates your `ProcessReceipt` handler [31]. | Yes — `MarketplaceService:PromptProductPurchase` (client) → `ProcessReceipt` server callback (set once, server script) → return `PurchaseGranted`/`NotProcessedYet`; validate PlayerId, ProductId, receipt status; use `UpdateAsync` to avoid double-grants [31][32]. | Dev product price 1 R$ – 1,000,000,000 R$; receipt contains the exact Robux paid even under price optimization; Roblox does not record per-user purchase history (you must) [31]. **Cross-game dev-product sales disabled 2026-05-30** → use Robux transfers [31]. |
| **Monetization — external (out-of-game) dev-product sales** | Test mode only (costs real Robux) [31] | Yes — products purchasable from the game's Store tab; `ProcessReceipt` fires when the user next enters the game; requires validated test mode + thumbnail; no paid-random/limited items externally [31]. | Same as above. |
| **Third-party APIs called from the client (LocalScript)** | Yes [33] | Yes technically — but **no secrets on the client** (Secrets store is server-only) [9], and client calls are forgeable; anything that grants value must be verified/forwarded by a server [1]. | Policy: outputs you deliver must comply with Community Standards; text chat must go through `TextChatService` (don't bypass safety measures) [34]. |
| **Streaming externally generated (AI) content into a game** | Yes (SSE `CreateWebStreamClient` is Studio-only) [2] | Yes via polling `HttpService:RequestAsync` [1]. Policy: third-party AI allowed; **you are responsible for outputs**; must disclose AI to users ("This is an AI-powered conversation, not human. It may make mistakes.") [34][35]; AI-interaction games need Content Maturity questionnaire disclosure; "extended AI interactions" (chatbots with memory) require the **Restricted (18+)** label [34]. | Free; model API costs on your side. |
| **"The game drives external agents" (game → backend → agents → GitHub)** | Yes (with local secrets / tunnel) | Yes — no official rule prohibits outbound automation from game servers to third-party services. Relevant constraints: AI disclosure rules [34][35], "Directing Users Off-Platform" (external URLs only via Social Links, 16+) [29], no off-platform sale of on-platform items for real money [29], and third-party apps may not "execute automated in game actions" on users' behalf via Open Cloud (API-key use for your own game is not affected) [36]. | N/A |

---

## (b) Recommended bridge shape: private validation loop (game → backend → agents → GitHub)

Goal: a personal, private loop where the Roblox game issues commands, a personal backend validates them, runs agents, and pushes results to a GitHub repo — then streams results back into the game.

```
Roblox game server (Script, ServerScriptService)
   │  1. HTTPS POST (public domain)
   │     headers: x-api-key: Secret from Secrets store [9]
   │     body:    {op, nonce, ts, payload}  (HMAC-signed, replay window)
   ▼
Personal backend (VPS, or home server behind Cloudflare Tunnel / ngrok w/ custom domain)
   │  - verify HMAC + timestamp (anti-replay)
   │  - enforce per-user quota from DevProduct credits [31][32]
   │  - dispatch to agents (local or cloud)
   │  - agents push to GitHub repo via REST git API (GitHub App installation
   │    token or classic PAT; fine-grained PATs vary per endpoint) [28][30]
   ▼
Back into the game (pick per payload size):
   a) Open Cloud Publish Universe Message  → MessagingService:SubscribeAsync  (≤1 KiB, near-real-time) [15][16]
   b) Data Store API entry / memory-store queue → game polls DataStoreService/MemoryStoreService (≤4 MB) [14][19]
   c) game polls backend over HttpService (stay well under 500 req/min/server) [1]
```

Design rules that follow directly from the sources:

1. **Everything server-side.** Secrets store is only readable by live servers (and collaborative testing); client scripts get "Can't find secret" errors [9]. All outbound calls go from a `Script` in `ServerScriptService`.
2. **Auth the backend on every request.** Official best practice: pre-shared secret; add HMAC(nonce + timestamp) so a leaked/recorded request can't be replayed [1].
3. **Private testing (Studio → personal backend):** for **Studio plugins** use localhost directly (explicitly supported [4][5]). For **in-game scripts**, do not rely on localhost/RFC1918 once published — the tunnel with a real domain is the portable path [1][community: 6]. Tunnels are fine because they are public HTTPS on allowed ports; use HTTPS, not free HTTP URLs [1][8].
4. **Push results via Open Cloud, don't poll the backend.** `publishMessage` is Stable and is the recommended replacement for the deprecated `/messaging-service/v1` endpoint [15][16][18]; message size is 1 KiB so use it for commands/status, data stores for payloads [14][16].
5. **Monetized credits:** DevProduct purchase (client prompt) → `ProcessReceipt` (server, idempotent via `UpdateAsync`) → grant credits → server signs a credit-consume request to the backend. Never trust the client to declare credit balances [31][32].
6. **GitHub account linking (if a user's GitHub identity is ever needed):** Roblox Open Cloud OAuth has an official **"Account Linking Tools"** app category with `openid` + `profile` scopes for mapping Roblox↔external accounts [36]; for GitHub itself use GitHub's **device flow** since the game cannot open a browser [27][28]. For the private loop, no user auth is needed — the backend's own GitHub token suffices.

**Verdict:** Everything needed for the private validation loop is officially supported: outbound HTTPS from game servers (500 req/min budget), a secrets store for credentials, a public-HTTPS backend reached via any tunnel/VPS, Open Cloud push-back into the game (messaging ≤1 KiB, datastores ≤4 MB), and a fully server-verified DevProduct credit economy. The only genuinely blocked/uncertain items: private-IP reachability from published servers (community consensus says blocked; not officially documented) and any official Roblox↔GitHub integration (does not exist). Roblox policy does not prohibit "game drives external agents"; it regulates the *content* (AI disclosures, Community Standards) and *commercial* plumbing (Robux-only, off-platform URL restrictions).

---

## (c) Sources (primary)

**Official Roblox docs (all verified 2026-08-02; docs updated 2026-07-31):**
1. In-game HTTP requests (HttpService) — limits, headers, ports, secrets, Open Cloud subset, best practices: https://create.roblox.com/docs/cloud-services/http-service
2. HttpService engine reference (rate limits, `CreateWebStreamClient` Studio-only, localhost Llama example): https://create.roblox.com/docs/reference/engine/classes/HttpService
3. Roblox staff announcement — HttpService port restrictions (Nov 15, 2021): https://devforum.roblox.com/t/port-restrictions-for-httpservice/1500073
4. HttpService doc, "Use in plugins" (localhost/127.0.0.1 support): https://create.roblox.com/docs/cloud-services/http-service#use-in-plugins
5. HttpService engine reference, `CreateWebStreamClient` code samples: https://create.roblox.com/docs/reference/engine/classes/HttpService#CreateWebStreamClient
6. DevForum — accessing localhost from Studio (community): https://devforum.roblox.com/t/how-to-access-localhost-using-httpservice-in-roblox-studio/1496085
7. DevForum — HttpService rate limiting / localhost while in Team Create (community): https://devforum.roblox.com/t/httpservice-rate-limiting-for-localhost-while-in-a-team-create/2137753
8. DevForum — HttpService↔external integrations incl. tunnels (community): https://devforum.roblox.com/t/voice-activated-dispatch-system-python-stt-to-roblox-httpservice-integration/4658286
9. Secrets stores (500/game, 1,024 chars, server-only, local secrets): https://create.roblox.com/docs/cloud-services/secrets
10. Open Cloud overview + feature index (what Open Cloud covers; no GitHub): https://create.roblox.com/docs/open-cloud and https://create.roblox.com/docs/cloud/reference
11. Full official docs index (zero GitHub pages; used to confirm no official GitHub integration): https://create.roblox.com/docs/llms.txt
12. OAuth 2.0 overview (authorization code + PKCE, OpenID Connect): https://create.roblox.com/docs/cloud/auth/oauth2-overview
13. Open Cloud rate limits (per-key-owner, per-token, `x-ratelimit-*`, 429 handling): https://create.roblox.com/docs/cloud/reference/rate-limits
14. Data and memory stores API (CRUD, versions, memory stores, API Key auth): https://create.roblox.com/docs/cloud/reference/features/storage
15. Universes API incl. `POST /cloud/v2/universes/{universe_id}:publishMessage`, `restartServers`, secrets endpoints: https://create.roblox.com/docs/cloud/reference/features/universes
16. Open Cloud Messaging usage guide (limits table: 1 KiB messages, 80-char topics, per-server/per-topic rates; topic created in Studio; OAuth scope `universe-messaging-service:publish`): https://create.roblox.com/docs/cloud/guides/usage-messaging
17. Notifications API (`POST /cloud/v2/users/{user_id}/notifications`): https://create.roblox.com/docs/cloud/reference/features/notifications
18. apis.roblox.com endpoint reference (messaging-service/v1 marked "Not Recommended"): https://create.roblox.com/docs/cloud/reference/domains/apis
19. Data store error codes and limits (4 MB object, throughput, storage formula): https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits
20. Places API (publish place versions): https://create.roblox.com/docs/cloud/reference/features/places
21. Assets API: https://create.roblox.com/docs/cloud/reference/features/assets
22. Developer Products API: https://create.roblox.com/docs/cloud/reference/features/developer-products
23. Luau Execution API: https://create.roblox.com/docs/cloud/reference/features/luau-execution
24. (see 11)
25. (see 10)
26. Rojo (third-party file↔Studio sync; the real "GitHub workflow" tool): https://github.com/rojo-rbx/rojo ; "Integrate Rojo into Roblox Studio officially" thread: https://devforum.roblox.com/t/integrate-rojo-into-roblox-studio-officially/657577
27. BrowserService engine reference (no documented methods — no in-game browser API): https://create.roblox.com/docs/reference/engine/classes/BrowserService
28. GitHub — Authorizing OAuth apps (device flow for headless apps; GitHub App recommendation): https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
29. Roblox Community Standards ("Directing Users Off-Platform", Roblox Economy, bots/automation): https://about.roblox.com/community-standards
30. GitHub — permissions required for fine-grained PATs (Git database endpoints under Contents): https://docs.github.com/en/rest/overview/permissions-required-for-fine-grained-personal-access-tokens
31. Developer Products (pricing 1–1e9 R$, ProcessReceipt, test mode, external sales, cross-game sales disabled 2026-05-30): https://create.roblox.com/docs/production/monetization/developer-products
32. MarketplaceService engine reference (ProcessReceipt signature/semantics): https://create.roblox.com/docs/reference/engine/classes/MarketplaceService
33. HttpService doc, "Enable HTTP requests": https://create.roblox.com/docs/cloud-services/http-service#enable-http-requests
34. Games with Generative AI (third-party AI responsibility, TextChatService, Content Maturity, Restricted label for extended AI): https://create.roblox.com/docs/generative-AI
35. Roblox Terms of Use (effective 2026-05-19; §8 AI Features, Creator Terms §6 AI tools/disclosures, prohibited ML training on Virtual Content): https://en.help.roblox.com/hc/en-us/articles/115004647846-Roblox-Terms-of-Use
36. Creator Third-Party App Policy (Account Linking Tools scopes `openid`/`profile`, prohibited automated in-game actions, data use rules): https://en.help.roblox.com/hc/en-us/articles/37924211313044-Creator-Third-Party-App-Policy

**Also cited:** https://create.roblox.com/docs/cloud/auth/api-keys (API keys, `x-api-key`, secrets management) — same URL family as [10].

### Uncertainty flags
- Private-IP (RFC1918) reachability from **published** servers: blocked per community consensus, not stated in official docs (official docs only document port and rate limits; the localhost example is Studio-oriented). Verify empirically with your own server before relying on it.
- Plain-HTTP (non-TLS) third-party endpoints: docs' engine examples still show `http://` URLs, but only HTTPS is guaranteed for Open Cloud calls; treat HTTP as deprecated/risky.
- Request/response body size limits for generic HttpService calls: not documented.
- Open Cloud "Luau Execution" endpoints exist but no guide describes their behavior — do not depend on them.
- Tunnel providers (ngrok/Cloudflare): no official allowance statement; compliant because they are public HTTPS on allowed ports. Free-tier HTTP URLs should be avoided.
