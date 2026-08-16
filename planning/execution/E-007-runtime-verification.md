# E-007 — Runtime verification (the "works first time" gate)

**Status:** pending (proposed next build)
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

Calibration step: test the verifier against known-good and known-broken
builds so we trust what it catches.

## Next eligible

E-008 — node/feature-graph architecture.
