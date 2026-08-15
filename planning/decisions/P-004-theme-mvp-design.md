# P-004 — Theme & MVP design (the whiteboard)

**Status:** current (planning)
**Depends on:** P-001, P-003

## Decision

The game's theme and the MVP's minimal scene. Work in progress — confirmed
so far by Drew (2026-08-15):

- **Theme: the whiteboard.** The player's workspace is a whiteboard;
  everything on it is a floating block you can grab and move (visual
  language from the diagram-design repo — blocks and connectors, no
  scenery).
- **No decoration.** The MVP only presents what is necessary to do the job.
  Simulation narration describes function, not atmosphere ("don't describe
  designs, describe what's needed to do the task").
- **One idea = a graph of builds.** Making money from an idea requires
  multiple connected builds (outreach system, video pipeline, landing
  page). The board shows idea block → connected build blocks; connections
  are automations (task-graph thinking from graph-engineering).
- **Money-first.** Every idea exists to make money; builds are the steps.
- **Content repurposing is a default build type** (blog/newsletter → social
  media), using the existing `faceless-explainer` skill family as the
  engine.

## Confirmed decision (Drew, 2026-08-15, option C + follow-up)

**The session plugin is the sandbox; the flow comes first, the game last.**
No fixed scene yet — the MVP is the session flow itself, text-based, and we
validate it by using it to make real repos. Visuals are minimal (clear
question + answer presentation now; plan visualization later). When the flow
produces working repos first-time reliably, THEN gamify it into Roblox.

- Theme ideas kept: whiteboard + floating blocks (diagram-design visual
  language) — for the eventual game, not the MVP.
- Philosophy: fun + real work; novel thing → test/brainstorm/be creative
  with usefulness and efficiency; "fun enough that I don't realize I'm
  building valuable software."
- Money-first: ideas exist to make money; automations (graph engineering)
  connect multiple builds per idea (outreach, video pipeline, landing
  page); content repurposing is a default build type (faceless-explainer
  family).
- No decoration: describe only what's necessary to do the job.

## The flow draft (session, text-based)

1. Enter — "the whiteboard" (one functional line).
2. Get an idea — Idea Finder (on demand) / card / custom / surprise.
3. Plan — A/B/C questions (set TBD) → precise plain-language plan summary.
4. Build — factory → real repo.
5. Result — repo link + cost + time; block "added to the board".
6. Next — another build for the same idea (the graph) or a new idea.

Validation loop: every run logs time/cost/first-try-success; we tune
questions, prompts, and flow from real use.

## Completion check

Flow draft exists; question set settled (next); simulation narration uses
the flow.
