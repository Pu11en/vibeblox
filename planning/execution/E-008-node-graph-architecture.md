# E-008 — Node/feature-graph architecture (solving the size limit)

**Status:** pending
**Depends on:** E-007, graph-engineering skill

## Outcome

Bigger products = a graph of small builds, not one big build:

- MVP = the system core (one build).
- Features = nodes that do one task (marketing, payments, pipeline) — each
  a separate build within the size limit, added on top of a working core
  (like n8n/Zapier nodes).
- The missing piece: the orchestration layer — shared config/env, a run
  command per node, ports, and the board that tracks idea → nodes → status.
- Task-graph thinking from the graph-engineering skill governs it
  (dependencies, parallel nodes, stop rule, human gates).

## Next eligible

board (persistent idea/build graph) → deploy web ideas → gamified shell.
