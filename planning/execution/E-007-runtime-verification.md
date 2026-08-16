# E-007 — Runtime verification (the "works first time" gate)

**Status:** complete (2026-08-15)
**Depends on:** E-001

## Outcome

The factory runs the generated project before shipping, not just syntax
checks:

1. **Static** (have it): py_compile / node --check, selene/stylua for game code.
2. **Runtime** (the build): execute the project in a sandbox with a timeout —
   run main, feed sample input, assert clean exit; for web builds, start the
   server and hit it with a request. A build that crashes does not ship.
3. **Generated tests**: for logic-heavy builds, the brain writes a small test
   file and it runs in the sandbox.
4. **Human acceptance**: Drew runs/opens the repo — the final gate.

Calibration done: unit-tested good/crash/infinite-loop/server cases,
shell-injection refusal, env scrub (keys never reach generated code), and a
live proof — Invoice Generator's first draft crashed at runtime, the machine
auto-fixed it, and it shipped (20s, $0.0008). Also fixed a CLI bug where the
run-command print had escaped the done branch (bailed early on running jobs).

## Next eligible

E-008 — node/feature-graph architecture.
