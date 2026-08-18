# Roblox Development — Tools, Workflow & Monetization (Research, Jul 2026)

Goal: build a Roblox experience (map/game) and earn real money from it. This doc is the
landscape of what's available in 2026, how the tools fit together, and what the pi coding
agent (running on WSL/Linux) can actually drive vs. what must happen in Roblox Studio on Windows.

---

## 0. The one hard fact first: WSL/Linux vs. Roblox Studio

- **Roblox Studio only runs on Windows or macOS.** It does not run on Linux/WSL.
  On this machine Studio lives on the **Windows host**; pi runs in WSL.
- That splits the work cleanly into two lanes:

| Lane | Where | Who | Examples |
|------|-------|-----|----------|
| **Code, structure, toolchain, codegen, procedural geometry, CI, asset prep** | WSL (Linux) | **pi** | write Luau, Rojo/Argon projects, run Selene/StyLua/Lune, generate `.rbxlx` place files, Blender headless, Open Cloud API uploads |
| **Visual map editing, playtesting, publishing, some asset uploads, Studio AI features** | Windows host | **you (in Studio)** | place parts, paint materials, import meshes, publish to a place, test in real client |

**The bridge:** a live-sync tool (Rojo or Argon) watches files on disk and pushes them into
Studio in real time. So pi edits `.luau` on disk → you see it appear in Studio instantly.
pi can also build a complete `.rbxlx` place file from a project (`rojo build`) with **no
Studio needed** — Studio is only required for publishing and visual work.

---

## 1. The toolchain (all installable on WSL via one manager: **Rokit**)

**Rokit** (by the rojo-rbx team) is the current standard toolchain manager. It installs and
pins versions per-project in `rokit.toml`. (Its predecessors **Foreman** and **Aftman** are
abandoned — don't use them.)

Install Rokit once, then declare tools per project:

```toml
# rokit.toml
[tools]
rojo   = "rojo-rbx/rojo@7.4.4"
wally  = "UpliftGames/wally@0.3.2"
selene = "Kampfkarren/selene@0.27.1"
stylua = "JohnnyMorganz/StyLua@0.20.0"
lune   = "lune-org/lune@0.8.x"
```

### Core tools (what each does — the "ton of tools")

| Tool | Purpose | pi uses it to |
|------|---------|---------------|
| **Rojo** | Filesystem ↔ Studio sync; builds `.rbxlx`/`.rbxm` from project | generate place/model files from code; sync scripts into Studio |
| **Argon** | Two-way **live** sync (Studio as editor, two-way), Rojo-compatible | preferred for editing — changes flow both ways in real time |
| **Azul** | Newest sync; treats **Studio as source of truth**, emits `sourcemap.json` | option if you build the map in Studio first, then code it |
| **Wally** | Package manager (npm-for-Roblox); `wally install` → `Packages/` | pull libraries (Knit, Fusion, Matter, Roact, etc.) |
| **Lync** | Layer over Wally; keeps packages updated | convenience layer |
| **Selene** | Static linter (Luau) | catch bugs/typos in CI and on save |
| **StyLua** | Code formatter | enforce consistent style |
| **Luau LSP** | Language server (autocomplete, go-to-def) | powers editor intelligence; reads Rojo `sourcemap.json` |
| **Lune** | Run Luau **outside** Studio (filesystem, HTTP, process, regex) | scripts: manipulate files/instances, codegen, fetch data, build assets |
| **Remodel** | Script Roblox file/instance ops (Luau API over `.rbxm`/`.rbxlx`) | batch-edit model files programmatically |
| **rbxmk** | Lower-level `.rbxm`/`.rbxlx` read/write/convert | convert formats, inject instances |
| **Tarmac** | Sync folders of images/textures → Roblox as assets, with manifest | manage bulk texture/sprite assets with stable IDs |
| **run-in-roblox** | Run a `.luau` script *inside* a Studio place headless | automated testing |
| **Mantle** | Declarative deployment (places, assets) via config + CI | publish/update experiences from CI without clicking Studio |
| **DarkLua** | Luau codegen/minify/path-rewrite | bundle, tree-shake, obfuscate before publish |
| **Moonwave** | Doc generator for Luau (llsuite-style) | generate API docs from code comments |
| **roblox-ts** | Compile **TypeScript → Luau** | optional if you'd rather write TS (opinion-divided; Luau is enough for most) |
| **TestEZ / Matter test / Rhodium / rbxts-jest** | Testing frameworks | unit + integration tests |

### Where they live / status
- All the above are open-source, actively maintained, and installable through Rokit
  (or `cargo install` / prebuilt binaries).
- One-command scaffolders exist: **`rblx-dev`** CLI sets up Rojo + Wally + Selene + StyLua +
  GitHub Actions CI + a working template (obby / simulator / rpg / tycoon).

---

## 2. Project structure (the Rojo/Argon layout)

A modern Roblox code project looks like:

```
roblox/
├── rokit.toml            # tool versions
├── wally.toml            # dependencies
├── default.project.json  # Rojo map: file tree → Studio DataModel
├── selene.toml           # linter config
├── .stylua.toml          # formatter config
├── .vscode/              # Luau LSP + sourcemap wiring
├── src/
│   ├── client/           → StarterPlayerScripts
│   ├── server/           → ServerScriptService
│   ├── shared/           → ReplicatedStorage
│   └── modules/
├── packages/             # Wally output (synced to ReplicatedStorage.Packages)
└── assets/               # textures/models/audio → Tarmac/Asset Manager
```

`default.project.json` is the contract that says *"this folder maps to this Studio service."*
pi writes this; Studio reflects it.

---

## 3. Building the map — four approaches (mix them)

1. **Manual in Studio (Windows).** You build the geometry with Studio's parts/terrain.
   Best for final art direction. pi can't do this directly.

2. **Procedural / code-generated (pi's sweet spot).** pi writes Luau that builds thousands
   of parts programmatically (terrain, mazes, city grids, obby stages, loot tables, instancing).
   Great for repeatable/reproducible maps and level generation.

3. **Blender → import.** Model in Blender, export `.fbx`/`.obj`/`.glb`, import as `MeshPart`.
   pi can drive Blender **headless** from WSL via its Python API (`blender --background --python`)
   to generate/remesh/texture models and export. (Blender isn't installed yet.)

4. **AI asset generation (2026 — very current).**
   - **Roblox Studio built-in:** Assistant (write code + generate simple 3D), Material/Texture
     Generator, AI mesh-from-text, and **Procedural Models** (code-defined 3D objects) rolling out.
   - **Third-party:** **Meshy** (native Roblox bridge, GLB one-click to Creator Hub),
     **3D AI Studio** (text/image → textured low-poly → FBX/OBJ), **3D-Agent** (Blender plugin),
     plus Tripo/KitsBlox/nilo. These run as web apps or Blender plugins — pi can feed them prompts
     and stage the exported files, even if the generation itself happens in-browser.

---

## 4. Asset pipeline & getting assets into the place

- **Textures/images/audio:** upload via Studio Asset Manager, or **Open Cloud API** (pi can do
  this with an API key) for bulk programmatic upload. Tarmac tracks them with stable asset IDs.
- **Meshes (.glb/.fbx/.obj):** import as MeshParts; the Bulk Importer splits multi-mesh files.
- **Moderation:** all assets pass Roblox moderation. Keep things original or clearly licensed.
- **Roblox Open Cloud API** (key-based, no Studio) lets pi: upload assets, publish place versions,
  run datastore/messaging ops, manage experiences — useful for an automated publish pipeline.

---

## 5. Making money (the actual goal)

### Revenue streams on Roblox
- **Game Passes** — one-time purchases for perks.
- **Developer Products** — consumables bought repeatedly (the workhorse of mobile-F2P monetization).
- **Premium Payouts** — paid based on **engagement time** from Premium subscribers (reward retention).
- **Immersive Ads / Sponsored experiences** — ad-revenue share, expanding in 2026.
- **Engagement-based payouts / Creator Rewards / Creator Fund** — bonuses for hitting milestones.
- **Creator Store** — sell templates, models, plugins, audio to *other* developers.

### DevEx — turning Robux into real cash (verified, current as of 2026)
- Earned Robux (from purchases, payouts, ad share, Creator Store) is cashed out via the
  **Developer Exchange Program**.
- **Eligibility:** ≥ **30,000 earned Robux**, 18+ (or with verified parent/guardian), Premium
  member, verified ID, in a supported country.
- **Current rate:** **$0.0038 per Robux** (= **$3.80 per 1,000 Robux**) for Robux earned after
  **Sept 5, 2025**. The old rate $0.0035/R$ applies only to pre-cutoff balances.
  → 30,000 R$ ≈ **$114**; 1,000,000 R$ ≈ **$3,800**.
- There are **regional/age rate tiers** (e.g. US 18+ vs other); confirm the exact tier for your
  country on the Creator Hub DevEx page before planning around a number.

### Realistic starter genres that monetize
Obby (obstacle course), Simulator, Tycoon, and RPG are the proven starter categories — and the
`rblx-dev` scaffolder ships templates for exactly these. The winning formula on Roblox is almost
always **short session + clear progress + a consumable to buy + social/loop retention**.

---

## 6. What pi can do right now vs. what needs you

**pi (WSL) can fully own:**
- Luau code for client/server/shared
- Project scaffolding (Rojo/Argon, Wally, Selene, StyLua, Luau LSP config)
- Procedural map/level generation in code
- Lune scripts for file ops, data fetching, codegen
- Running linter/formatter/tests in CI
- Blender-headless model generation/export (once Blender installed)
- Open Cloud API asset upload & publish automation (with API key)
- Building `.rbxlx` place files via `rojo build`

**Needs you (Windows + Studio):**
- Final visual placement & art direction
- Playtesting in the real Roblox client
- Publishing the experience to a live place (first publish must be manual)
- Studio-only AI features (Assistant mesh gen, material/texture generator)
- Anything requiring a logged-in Studio session

**Not yet installed (would need adding):** Rokit + the toolchain, Blender (for the 3D lane), and
optionally a Roblox account API key for Open Cloud. None are installed yet.

---

## 7. Recommended starter stack & next step

Minimum viable professional setup:
1. **Rokit** → installs Rojo, Wally, Selene, StyLua, Lune (one install, all pinned).
2. **Argon** for two-way live sync into Studio (Rojo-compatible).
3. **Luau LSP** in the editor for autocomplete (reads Rojo sourcemap).
4. A **genre template** (obby/sim/tycoon) via `rblx-dev` or a hand-rolled Rojo skeleton.
5. **Blender** (later) if you want custom meshes; **Open Cloud API key** (later) for automated uploads.

Proposed concrete next deliverable: scaffold a new Roblox project in this folder with Rokit +
Rojo/Argon + Wally + Selene/StyLua wired up and a working starter genre, so pi can immediately
start writing Luau and you can open it in Studio on Windows.

(Confirm the genre — obby / simulator / tycoon / something else — and say "go" to build it.)
