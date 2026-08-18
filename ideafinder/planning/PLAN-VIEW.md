# GITBUTT next round

**Status:** awaiting approval

**Destination:** an approved worklist: test what is built, finish the catalog.

**Success:** themed idea run returns a real pitch; zero unclassified repos; wiki regenerated.

**Now:** final review of the finished plan.

**Next:** approval, then E-001 starts.

```mermaid
flowchart LR
    P1(["NOW · E-001 Test the tool live"])
    P2["2 · E-002 Finish the catalog"]
    D(["DONE · Round complete"])
    P1 --> P2 --> D

    classDef current stroke-width:3px,font-weight:700;
    classDef milestone stroke-width:2px;
    classDef proof stroke-width:3px,font-weight:700;

    class P1 current;
    class P2 milestone;
    class D proof;
```

**Text route:** Goal → test the tool live (one themed idea run) → finish the
catalog (label 273 repos, regenerate wiki) → done.

## Step details

<details open>
<summary>1 · Test the tool live (E-001)</summary>

- Outcome: one themed idea run returns a real pitch; read-only tools demoed.
- Owner: agent
- Inputs: P-001, skill guide
- Proof: idea output, ruff passes, build succeeds
- If blocked or changed: report the error; code fixes beyond trivial return to planning

</details>

<details>
<summary>2 · Finish the catalog (E-002)</summary>

- Outcome: zero unclassified repos; wiki regenerated.
- Owner: agent
- Inputs: existing data, taxonomy
- Proof: status shows none missing; wiki pages updated
- If blocked or changed: report; don't force poor labels

</details>

## Plan-wide safety

- Nothing runs automatically; every run is an approved session action.
- Quota and mutation jobs run only after Drew approves them.
- Never print, share, or commit `.env`.
- Preserve `data/repos.sqlite3`.
- GITBUTT stays standalone; never touch channel-brains.
- Keep describing GITBUTT as a local prototype.

Details: [plan](PLAN.md) · [decision](decisions/P-001-next-round-scope.md) · [E-001](execution/E-001-test-the-tool-live.md)
