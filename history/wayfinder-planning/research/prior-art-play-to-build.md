# Prior art: "playing a game IS doing real work with AI"

**Research ticket:** Wayfinder — validate novelty of a Roblox tycoon where in-game actions drive a real external agent backend, and completing a "project" produces a real artifact (e.g., a real GitHub repo with real code).
**Date:** 2026-08-02
**Method:** Web searches against primary/high-trust sources (official docs, papers, product pages, repos), with key pages fetched and verified directly. Every claim below is linked to its source; sources with a fetch check are marked `[verified]`.

---

## TL;DR verdict

- **The conceptual claim "playing a game can be real work" is old and extremely well-proven** — human-computation games (ESP Game, Foldit, EVE Online's Project Discovery) produced real scientific artifacts at massive scale, and Roblox experiences have called real third-party APIs for years.
- **The specific combination — a consumer Roblox experience whose core loop drives an external AI-agent backend and whose output is a real artifact for the player (real repo, real code) — has no shipped prior art found.** The closest thing is Tycono (a tycoon-style UI over agents that write real code), which is a developer tool for programmers, not a game for a Roblox audience.
- **Policy wall to design around:** Roblox's Terms of Use strip Robux/virtual content of real-world value and prohibit off-platform real-world transactions; the sanctioned real-money flows are creator-side (DevEx, paid access, commerce providers). Players producing artifacts into *their own* external accounts is a different lane than selling artifacts, but it is still a policy-sensitive design.

---

## 1. Roblox experiences wired to REAL external work

### 1.1 Technical substrate — this is shipped, normal practice

Roblox experiences can make real HTTP calls to any external third-party API via `HttpService` (server-side; must be enabled in experience settings). The official API reference shows examples calling `api.open-notify.org`, Google Gemini, `httpbin.org`, even `localhost`, plus Roblox's own Open Cloud endpoints. [verified: https://create.roblox.com/docs/reference/engine/classes/HttpService]

Community guides document the standard use cases: external leaderboards, real-time weather/stock/sports data, Discord webhooks, auth backends. [https://roblox.club/httpservice-api-complete-roblox-guide-for-web-requests-external-api-integration-in-2025/]

**Implication:** a Roblox experience driving a live external backend (the agent runner) is technically mundane — the platform explicitly supports it.

### 1.2 Shipped experiences consuming real third-party data

- **StockRise** — Roblox's highest-grossing stock simulator; "hyper-realistic paper trading" with **real-time stock and crypto prices**; 7M+ plays, 10.9 min average session. Acquired by PiP World (Aug 2024) as a funnel into a blockchain play-to-earn ecosystem (PiP Trader, Gold Rush on Telegram). Roblox itself was an investor. [GamesBeat: https://venturebeat.com/games/pip-world-acquires-high-grossing-stock-simulator-game-stockrise/ (title/facts confirmed via search; fetch rate-limited 429, not 404); PitchBook profile confirms Aug 7 2024 acquisition]
- **Trading Empire, Investor Center, Wall Street Tycoon** — more stock/crypto experiences with "REAL price charts" and live player-driven markets. [RobloxGo listings via search, 2026]
- These are **read-only** integrations (real data in, virtual game state out) — the real world informs the game; the game does not act on the real world.

### 1.3 Live LLM APIs inside Roblox experiences

Multiple open-source projects wire real GPT/Claude APIs into experiences and Studio (all require enabling HTTP requests and bringing your own API key):

- NPC dialogue systems calling OpenAI GPT-3.5/GPT-4o from in-experience server code: [https://github.com/rockuutree/roblox-ai-dialogue], [https://github.com/samhback/chatgpt-assistants-to-roblox], [https://github.com/0x600/ChatGPT-Commands]
- GPT-3 NPCs in a playable experience (conversation + natural-language in-game actions): [https://github.com/JavaFXpert/roblox-gpt3-game]
- Your character becomes an agent that moves/talks/acts via the Chat Completions API: [https://github.com/snipcola/Roblox-AI]
- Studio-side AI code generation plugins (GPT-4/Claude/Gemini): [https://github.com/classifiedcoach/RoPilot-A-Roblox-Plugin-that-writes-and-implements-code-for-you]

These prove live external AI calls from Roblox are done routinely — but output stays inside the game; nothing is pushed back out.

### 1.4 Official real-world money/goods flows (the sanctioned lanes)

- **DevEx** — creators convert earned Robux to real cash (minimum 30k earned Robux; W-9/W-8; rate ~$350/100k Robux per PCMag via search). Roblox paid creators **$1B+ via DevEx** in the 12 months ending June 2025. [Roblox monetization docs: https://create.roblox.com/docs/production/monetization]
- **Paid Access in real currency** (announced RDC 2024): paid experiences priced in real dollars on desktop, revenue shares 50%/60%/70% at $9.99/$29.99/$49.99. [official newsroom: https://d3fel7ao8ljmgc.cloudfront.net/en-au/newsroom/2024/09/rdc-2024-robloxs-next-frontier]
- **Shopify commerce partnership** (RDC 2024): eligible creators sell **physical merchandise inside experiences** (real goods, real dollars, third-party checkout). [same newsroom URL]
- **PLS DONATE** — the archetypal "real money flows through gameplay" experience: ~5.17B visits; players donate real Robux (gamepass/UGC purchases) to each other at booths; dev takes a ~10% commission; big donations trigger global spectacle effects (blimp, nuke, smite, starfall). [verified: https://roblox.fandom.com/wiki/PLS_DONATE]

### 1.5 The policy wall

Roblox ToS (verified by direct fetch): "Robux are not a substitute for real currency", "Robux cannot be redeemed for any real currency", "Virtual Content has no real world equivalent value", and off-platform Robux/virtual-content transactions via third-party services are a violation. Cross-trading real-life items/currency for Robux is treated as scamming. [https://en.roblox.com/info/terms-of-use]

**Explicit gap for category 1:** *No shipped Roblox experience found whose gameplay pushes real output to an external service on the player's behalf* (no real GitHub repos, no real accounts written to). The closest shipped lanes are read-only live data (StockRise), in-game LLM calls (dev templates), and real-money commerce that stays inside Roblox's own rails (DevEx, paid access, PLS DONATE, Shopify merch). A player-facing "your play produced a real external artifact" loop is not present in the shipped record.

---

## 2. Games/projects that gamify REAL coding or AI work

### 2.1 Play = real code as the game's core artifact

- **Screeps** — open-source MMO RTS where your units are controlled by **real JavaScript you write**; the code runs 24/7 in a persistent world shared with other players ("programming your units' AI", runs even while offline). Your code is the game's central persistent artifact; the world has run for a decade on some bots. [Steam: https://store.steampowered.com/app/464350/Screeps_World/ ; architecture: https://docs.screeps.com/architecture.html ; wiki: https://wiki.screepspl.us/Getting_Started]
- **Bitburner** — open-source incremental "hacking" game scripted in **real JavaScript/TypeScript**; player scripts are real files, widely shared and versioned in public GitHub repos (66 public repos under the topic). [Steam: https://store.steampowered.com/app/1812820/Bitburner/ ; https://github.com/topics/bitburner]

Note the boundary: in both, the code's only consumer is the game itself — the artifact is real code, but it doesn't leave the game's domain.

### 2.2 Gamified real AI/ML work — Kaggle

Kaggle competitions are games (leaderboards, ranks, prizes, progression) whose output is **real, production-usable predictive models**. Documented case: Boehringer Ingelheim's gamified challenge produced models "as good, if not better" than academic community models in ~3 months, with winning code used in drug development. Research on Kaggle also documents the failure mode: public-leaderboard overfitting (Blum & Hardt, "The Ladder" — adaptive resubmission; split public/private boards only partially fix it). [https://www.kaggle.com/competitions ; https://arxiv.org/abs/1411.0207]

### 2.3 Gamified real dev work with real payouts — Gitcoin

Gitcoin bounties attach crypto payouts to real GitHub issues; contributors' merged code is the artifact, escrow-backed, with gamified quests/kudos/hackathons; ~$3.5M+ paid in bounties since launch. [https://gitcoin.co]

### 2.4 Play = real scientific work (the "games with a purpose" lineage) — the strongest "play IS work" evidence

- **ESP Game** (von Ahn & Dabbish, CHI 2004) — two strangers label the same image; agreement = label. Over 1M labels in 4 months; Google licensed it as Google Image Labeler. The founding paper of "games with a purpose"; real training data was the byproduct of play. [http://dx.doi.org/10.1145/985692.985733]
- **Foldit** (UW Center for Game Science) — players fold **real proteins**, scored by the Rosetta energy function (an automated metric that correlates with real quality — borrowable!). Results published: 2010 Nature proof-of-concept; 2011 solved the M-PMV retroviral protease structure that had eluded scientists for a decade; 2012 enzyme redesign; 2019 *de novo* protein design — 56 player designs folded into stable proteins in the lab. [https://doi.org/10.1038/nature09304 ; https://doi.org/10.1038/nsmb.2119 ; https://doi.org/10.1038/nbt.2109 ; https://doi.org/10.1038/s41586-019-1274-4]
- **EVE Online: Project Discovery** — a mini-game inside a commercial MMO where players classify **real scientific data** (Human Protein Atlas microscopy images; CoRoT exoplanet light curves): ~322k players, ~33M classifications in year one; results published in Nature Biotechnology (2018), combined with deep learning (Loc-CAT); researcher Emma Lundberg appeared as an in-game NPC. Explicit evidence that *a mass-market game embedding real work attracts and retains players* (1.9M participants, ~1B classifications across phases). [https://doi.org/10.1038/nbt.4225 ; lineage overview: https://en.m.wikipedia.org/wiki/Game_with_a_purpose]
- Same lineage (EteRNA, Eyewire, Zooniverse) — see the GWAP overview link above.

### 2.5 Play = real-world impact without code

- **Freerice** (WFP): correct answers trigger sponsor-matched donations (10 grains rice-equivalent per answer, ~$1.5–1.8M raised, 100% to WFP). [https://freerice.com]
- **Habitica**: your **real-world tasks** are the input; completion grants XP/gold/quests — the game progress is a mirror of real work done outside the game (no artifact produced by the game). [https://habitica.com]

**Explicit gap for category 2:** *No shipped "tycoon/management-game skin over actual AI-agent runs" aimed at players exists* — the only entry found is Tycono (category 3, developer-facing). Coding games to date either keep the code inside the game (Screeps, Bitburner, CodinGame/Codewars) or keep the work as exercise/competition (Kaggle, Gitcoin) rather than "you play → an agent builds → you get the artifact."

---

## 3. AI-agent game layers

### 3.1 Tycono — the closest prior art to the whole concept

Tycono is an open-source platform (`npx tycono`) that **"turns multi-agent AI into a game-like visual"** — and its origin story is almost exactly the idea being validated:

> "**Tycono started as an AI office tycoon game** — pixel characters walking around, sitting at desks, chatting in Slack-like channels. The underlying agents proved genuinely useful (writing real code/documents), so the developers stripped the pixels and built a terminal tool. The pixel office survives as `npx tycono --classic`."

- Agents do **real work**: CEO dispatches orders down an org tree (CEO → CTO → Engineers → QA), roles have scoped authority, knowledge compounds across sessions; output is real code/docs. "Company-as-Code" — org in YAML/Markdown, versionable/forkable.
- **What it lacks vs. the Roblox idea:** it's a dev tool for developers (needs Node + Claude Code CLI), runs on your machine, has no player audience/economic loop, no Roblox presence, no artifact hand-off to non-programmers, no monetization. The game layer is decoration around a CLI, not the product. [verified Product Hunt: https://www.producthunt.com/p/tycono ; npm: https://www.npmjs.com/package/tycono ; GitHub: https://github.com/seongsu-kang/tycono]

### 3.2 Tycoon AI (tycoon.us) — gamified name, non-game product

"Run a one-person company entirely with AI agents" — AI CEO "Astra" plans, assigns agents (CMO, CTO who codes — pushes code to GitHub via Claude Code), tracks progress, asks for approval. **Not a game**: no gameplay, no gamification on the product page; a real operating tool for solo founders. [verified: https://www.producthunt.com/products/tycoon-us]

### 3.3 Cosmetic overlays on agentic coding (fun around the work, no real output)

- **Tokengotchi** — idle RPG powered by your Claude Code/Codex/Gemini token logs; cosmetic only ("nothing leaves your machine"); anti-pay-to-win, streak-weighted. [verified: https://www.npmjs.com/package/tokengotchi]
- **RPGDev** — desktop JRPG overlay: Codex CLI / Claude Code hook events become battle actions, TODO list becomes a quest log. [verified: https://www.npmjs.com/package/rpgdev]
- Others surfaced by search, not fetch-verified: **Prompt Warrior** (character-sheet/achievements from agent session logs), **VibeSense** (drive the agent with a game controller + snake minigame), **Agent Academy** (spy-themed TUI for practicing Claude Code patterns). All are cosmetic/practice layers — the game never changes the work or the output.

### 3.4 Agent-vs-agent games with real code output

**Jianghu** — browser 1v1 wuxia dueling game where your AI coding agent (Claude Code, Codex, Cursor) writes a real JavaScript combat function; leaderboard of agents; QuickJS sandbox. Real code is the game piece, but it's a tournament arena, not a work-producing loop. (Surfaced via search; not fetch-verified.)

### 3.5 Reverse direction: the agent plays the game

**OpenRCT2 + Claude Code** experiment — Claude Code runs inside RollerCoaster Tycoon 2, managing the park through a purpose-built CLI/JSON-RPC. Fun inversion, but here the agent is the player, not the backend doing the player's work. [https://github.com/jaysobel/OpenRCT2/blob/coding-agent/CODING_AGENT.md]

### 3.6 The "virtual software company" metaphor at the agent level

- **ChatDev** (OpenBMB/Tsinghua, ACL 2024) — "virtual chat-powered software company": CEO/CPO/CTO/programmer/test engineer agents converse through waterfall phases and produce real code; ~17 files per project in <7 min for ~$0.30. [https://arxiv.org/abs/2307.07924 ; https://github.com/OpenBMB/ChatDev]
- **MetaGPT** (DeepWisdom) — "GPT acts as a software company": PM/Architect/PM/Engineer/QA roles, SOPs, "Code = SOP(Team)"; real code output, ~$2/project. [https://arxiv.org/html/2308.00352v6 ; https://github.com/FoundationAgents/MetaGPT]

The company/organization metaphor over multi-agent coding is established research practice — but these are agent-side frameworks; no human player sits in the org chart.

**Explicit gap for category 3:** *No shipped product wraps planning/ticketing/execution of agentic coding in playable gameplay for non-programmers with the game as the primary interface and the artifact as the prize.* Tycono is the lone near-miss, and it explicitly pivoted away from the game toward a CLI.

---

## 4. Gamification of AI-assisted development: shipped and attempted

### 4.1 Shipped by vendors

- **GitHub Achievements** (2022–) — badges for real work: merged PRs (Pull Shark), stars, co-authored commits, Discussions answers, sponsors. Real activities, cosmetic reward. [community guide: https://github.com/SMatvii/GitHub_Achievements]
- **Claude Code ships deliberately gamified UX** — the terminal includes an animated token counter, subagent spin-up theatrics, a `/radio` lofi station (Claude FM — an official built-in command, launched as an easter egg), and a `/buddy` terminal pet with 18 species, rarities, and stats. Widely commented on: Theo Browne (t3.gg) — "They engineered it to be like a slot machine... as much a marketing tool as a developer tool." Anthropic gamified the *feel* of agentic coding at the top end of the market. [Anthropic docs: https://docs.anthropic.com/en/docs/claude-code ; source repo incl. changelog: https://github.com/anthropics/claude-code ; commentary: https://t3.gg]
- **VS Code gamification ecosystem** — Code::Stats (XP for keystrokes, [https://codestats.net]), plus DevGotchi (RPG pet, "Bug Boss" tied to real lint errors), Coding Achievements, Expcode, Codamine (marketplace extensions surfaced via search). All cosmetic overlays on real coding.

### 4.2 Academic evidence on effectiveness (mixed-to-negative)

Calefato, Quaranta & Lanubile, *Information and Software Technology* 176 (2024): analysis of 6,000+ developers after GitHub's badge launch — badges **don't reliably signal skill**, had **no measurable effect on activity** (except star-linked Starstruck), and a **growing number of users opt out** by hiding profiles. Community reaction: appealing "in principle," purposeless in practice. [https://doi.org/10.1016/j.infsof.2024.107561 ; preprint: https://arxiv.org/abs/2303.14702]

**Lesson:** badge-ware alone fails; gamification only sticks when it's tied to something the player values that the badges don't proxy (Project Discovery's "your data got published", Foldit's "you solved a 10-year-old structure", Screeps' "your bot dominates shard 3").

### 4.3 Failed/attempted signals

- The ESP Game paper was **rejected from CHI** before the working game proved the idea — the proof was the artifact, not the pitch. [https://dl.acm.org/doi/fullHtml/10.1145/1869086.1869102]
- Kaggle's documented overfitting failure mode (public leaderboards gamed until solutions fail to generalize) is the canonical "game rewards wrong thing" lesson. [https://arxiv.org/abs/1411.0207]
- No major shutdowns of play-to-code products were found to cite — the category barely exists, which is itself the finding.

---

## 5. Verdict: what exists vs. what is genuinely novel

**Exists (proven):**
1. Roblox → external APIs: shipped practice (HttpService; StockRise; GPT-NPC experiences).
2. Play = real work: proven at massive scale (ESP Game, Foldit, Project Discovery, Freerice, Habitica).
3. Games whose artifact is real code: Screeps, Bitburner (code stays in-game); Kaggle, Gitcoin (artifact is the deliverable, gameplay is thin).
4. Game layers over AI coding agents: Tycono (tycoon skin, real work, dev audience), Tokengotchi/RPGDev/etc. (cosmetic), Jianghu (agent code as game piece).
5. Real-money rails on Roblox: DevEx, real-currency paid access, Shopify merch, PLS DONATE.

**Genuinely novel (no shipped prior art found):**
- A **consumer-facing Roblox game** (tycoon genre) whose core loop is *orchestrating a real external agent backend*, where completing an in-game "project" yields a **real external artifact owned by the player** (real GitHub repo, real code, real CI), for an audience of players rather than developers.
- Specifically novel in combination: (a) Roblox as the venue/audience + (b) gameplay-as-agent-orchestration (not a skin over an IDE) + (c) artifact delivery out of the game to the player's own accounts + (d) a monetization loop around that (see borrowables).
- Caveat: Tycono demonstrates every *conceptual* ingredient except the Roblox venue, the non-programmer audience, the artifact hand-off as the product, and the economic loop. The novelty claim should be scoped as "first to combine these into one shipped product on Roblox," not "no one has ever thought of a tycoon game about AI."

---

## 6. What to borrow

**Mechanics**
- Project Discovery's model: real task + in-game rewards + narrative framing ("Drifter DNA") + researcher NPCs + published results — turns "we used your work" into content. An equivalent: finished agent projects feed a visible in-game gallery, leaderboards, and player credits.
- Foldit's automated quality score (Rosetta energy) — the game scores what real science validates. Equivalent: every project has a real acceptance gate (repo created, CI green, tests pass, README done) — the game's "quality bar" IS the real verification. This also makes "completed project" a precise, escrow-able definition (Gitcoin's acceptance-criteria model).
- PLS DONATE's donation spectacle (blimp → nuke → smite at increasing thresholds) — a proven Roblox pattern for escalating, shareable celebrations. Reuse for project completion tiers (first PR, first green CI, first deployed app).
- Tycono's org-tree dispatch (CEO → CTO → engineers, scoped authority) as the tycoon's management layer — the hire/upgrade loop of the tycoon genre maps 1:1 onto agent roles and capabilities.
- Screeps' persistent-world gravity: "your repo is live in the world" keeps players coming back; an artifact gallery that keeps growing works the same way.

**UX**
- Badges/achievements only as secondary signals — the Calefato study says badge-only layers don't move behavior; the artifact and its use in the world must be the reward.
- Keep agent actions legible (Project Discovery made the scientific task comprehensible to 13-year-olds; agent planning/ticketing must be shown as simple "quests" with progress, not logs).

**Monetization patterns**
- PLS DONATE commission model: take a cut of in-game Robux flows (e.g., players buy "project slots"/"agent boost" with Robux) rather than selling the artifact.
- Roblox real-currency paid access / premium tiers (50–70% rev share at $10–50) — fits a "premium studio" or subscription-style tier (more agent capacity, private repos).
- Freerice sponsor-matching as an alternative: compute costs sponsored → players play free, sponsors pay.
- DevEx is the eventual creator-side conversion, but per ToS, never sell the real artifact itself for Robux (see policy).

**Verification (critical)**
- Kaggle's overfitting lesson: keep acceptance criteria hidden/verified — don't let the game's visible progress proxy for quality; real gates (CI/tests/deploy) are the private leaderboard.
- Gitcoin-style escrow: payouts/rewards release only on verified acceptance.

**Policy caution**
- ToS: virtual content has no real-world value; off-platform transactions for Robux are violations. Deliver artifacts to the player's *own* external accounts (free GitHub repos) rather than transferring value inside Roblox; monetize throughput/vanity, not artifacts. (This is the biggest open design question for the concept — worth a policy review before building.)

---

## 7. Sources

**Roblox platform (category 1)**
- Roblox HttpService API reference — https://create.roblox.com/docs/reference/engine/classes/HttpService [verified via fetch]
- HttpService external-integration guide — https://roblox.club/httpservice-api-complete-roblox-guide-for-web-requests-external-api-integration-in-2025/
- GamesBeat: "PiP World acquires high-grossing stock simulator game StockRise" — https://venturebeat.com/games/pip-world-acquires-high-grossing-stock-simulator-game-stockrise/ (facts confirmed via two independent searches; fetch rate-limited)
- Roblox Newsroom, RDC 2024: "Roblox's Next Frontier" (paid access real currency; Shopify merch) — https://d3fel7ao8ljmgc.cloudfront.net/en-au/newsroom/2024/09/rdc-2024-robloxs-next-frontier
- Roblox Terms of Use (Robux no real-world value; off-platform transactions prohibited) — https://en.roblox.com/info/terms-of-use [verified via fetch]
- Roblox monetization docs (DevEx) — https://create.roblox.com/docs/production/monetization
- PLS DONATE wiki — https://roblox.fandom.com/wiki/PLS_DONATE [verified via fetch]
- LLM-in-Roblox repos: https://github.com/rockuutree/roblox-ai-dialogue · https://github.com/samhback/chatgpt-assistants-to-roblox · https://github.com/JavaFXpert/roblox-gpt3-game · https://github.com/0x600/ChatGPT-Commands · https://github.com/snipcola/Roblox-AI · https://github.com/classifiedcoach/RoPilot-A-Roblox-Plugin-that-writes-and-implements-code-for-you

**Play = real code / real work (category 2)**
- Screeps: Steam — https://store.steampowered.com/app/464350/Screeps_World/ · architecture — https://docs.screeps.com/architecture.html · wiki — https://wiki.screepspl.us/Getting_Started
- Bitburner: Steam — https://store.steampowered.com/app/1812820/Bitburner/ · repos — https://github.com/topics/bitburner
- Kaggle — https://www.kaggle.com/competitions · Blum & Hardt, "The Ladder: A Reliable Leaderboard for Machine Learning Competitions" — https://arxiv.org/abs/1411.0207
- Gitcoin — https://gitcoin.co
- von Ahn & Dabbish, "Labeling Images with a Computer Game" (CHI 2004) — http://dx.doi.org/10.1145/985692.985733 · von Ahn profile/backstory — https://dl.acm.org/doi/fullHtml/10.1145/1869086.1869102
- Foldit: Cooper et al. 2010 (Nature) — https://doi.org/10.1038/nature09304 · Khatib et al. 2011 (Nat Struct Mol Biol) — https://doi.org/10.1038/nsmb.2119 · Eiben et al. 2012 (Nat Biotech) — https://doi.org/10.1038/nbt.2109 · Koepnick et al. 2019 (Nature) — https://doi.org/10.1038/s41586-019-1274-4
- EVE Project Discovery paper (Nat Biotech 2018) — https://doi.org/10.1038/nbt.4225 · GWAP lineage — https://en.m.wikipedia.org/wiki/Game_with_a_purpose
- Freerice (WFP) — https://freerice.com · Habitica — https://habitica.com

**AI-agent game layers (category 3)**
- Tycono — https://www.producthunt.com/p/tycono [verified] · https://www.npmjs.com/package/tycono · https://github.com/seongsu-kang/tycono
- Tycoon AI — https://www.producthunt.com/products/tycoon-us [verified]
- Tokengotchi — https://www.npmjs.com/package/tokengotchi [verified] · RPGDev — https://www.npmjs.com/package/rpgdev [verified]
- OpenRCT2 + Claude Code experiment — https://github.com/jaysobel/OpenRCT2/blob/coding-agent/CODING_AGENT.md
- ChatDev — https://arxiv.org/abs/2307.07924 · https://github.com/OpenBMB/ChatDev
- MetaGPT — https://arxiv.org/html/2308.00352v6 · https://github.com/FoundationAgents/MetaGPT

**Gamification of AI-assisted dev (category 4)**
- GitHub Achievements guide — https://github.com/SMatvii/GitHub_Achievements
- Calefato, Quaranta & Lanubile 2024 (Information and Software Technology) — https://doi.org/10.1016/j.infsof.2024.107561 · preprint — https://arxiv.org/abs/2303.14702
- Claude Code (docs, repo incl. changelog) — https://docs.anthropic.com/en/docs/claude-code · https://github.com/anthropics/claude-code
- Theo Browne (t3.gg) on Claude Code's gamified UX — https://t3.gg
- Code::Stats — https://codestats.net

**Not fetch-verified (surfaced via web search only, included for completeness):** Prompt Warrior, VibeSense, Agent Academy, Jianghu (agent-game wrappers); RobloxGo listings for Trading Empire / Investor Center; PCMag DevEx rate figures; PitchBook StockRise acquisition profile.
