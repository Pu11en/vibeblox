# Roblox Materials — Complete Research (Jul 2026)

"Materials" in Roblox = the surface look of any `BasePart` or `Terrain` voxel. This doc covers:
the **full built-in material list**, how to customize them (**MaterialVariant** + **MaterialService**),
**PBR SurfaceAppearance** for meshes, texture specs, **where to get free materials**, AI generation,
and what pi can do with all of it.

---

## 1. The complete built-in material list (Enum.Material — 45 materials, 2026)

Source: Creator Hub engine enum (current). Every `BasePart` has a `Material` property set to one of these.
Grouped by what they look like and typical use:

### Smooth / plastic / glass / glow
| Material | Use |
|---|---|
| **Plastic** | The default; matte neutral surface |
| **SmoothPlastic** | Plastic without the subtle bumps — totally flat matte |
| **Neon** | Self-emissive, glowing; ignores lighting, great for signs/trails/lava-glow |
| **ForceField** | Animated energy-shader (the classic shield look) |
| **Glass** | Transparent + refractive; color = tint |

### Metal
| Material | Use |
|---|---|
| **Metal** | Clean generic metal |
| **DiamondPlate** | Tread-plate / industrial nonslip pattern |
| **CorrodedMetal** | Rusted, weathered metal |
| **Foil** | Bright, crinkled foil look |

### Wood
| Material | Use |
|---|---|
| **Wood** | Solid plank grain |
| **WoodPlanks** | Visible separated planks |

### Stone / masonry
| Material | Use |
|---|---|
| **Concrete** | Flat concrete |
| **Slate** | Layered slate rock |
| **Marble** | Polished veined marble |
| **Granite** | Speckled granite |
| **Brick** | Brick wall pattern |
| **Pebble** | Small pebbles |
| **Cobblestone** | Rounded cobble path |
| **Rock** | Natural rough rock |
| **Basalt** | Dark volcanic rock |
| **Limestone** | Pale sedimentary stone |
| **Pavement** | Paved/sidewalk surface |
| **Sandstone** | Layered sandy stone |

### Ground / outdoor
| Material | Use |
|---|---|
| **Grass** | Short mowed grass |
| **LeafyGrass** | Grass with leaves/undergrowth |
| **Sand** | Beach/desert sand |
| **Snow** | Snow |
| **Mud** | Wet mud |
| **Ground** | Bare dirt |
| **Asphalt** | Road asphalt |
| **Salt** | Salt flat / crusty white |

### Ice / water / lava
| Material | Use |
|---|---|
| **Ice** | Solid slippery ice |
| **Glacier** | Deep translucent glacial ice |
| **Water** | Translucent animated water (also the Terrain water material) |
| **CrackedLava** | Dark crust with glowing magma cracks (emissive) |

### Special
| Material | Use |
|---|---|
| **Air** | No collision/visual (used in Terrain to carve) |

### Fabric / flooring / organic (newest batch, values 2304–2311)
| Material | Use |
|---|---|
| **Fabric** | Woven cloth |
| **Cardboard** | Cardboard |
| **Carpet** | Carpet flooring |
| **CeramicTiles** | Tiled ceramic floor/wall |
| **ClayRoofTiles** | Terracotta clay roof tiles |
| **RoofShingles** | Asphalt roof shingles |
| **Leather** | Leather |
| **Plaster** | Wall plaster |
| **Rubber** | Rubber |

> Terrain uses its own `Terrain:FillBlock()` material enum but the same names apply (plus Terrain-exclusive
> behavior for Water/Air). pi can generate terrain programmatically with any of these.

---

## 2. How materials actually work

- A `BasePart.Material` selects the look. Each material also has a hidden **physical** behavior
  (Friction, Elasticity, Density) — e.g. Ice is slippery, Rubber is bouncy, Metal is dense.
- **Color** (`BrickColor` / `Color`) multiplies the material's texture, so `Snow` + blue tint = blue snow.
- **Transparency** and **Reflectance** layer on top of the material.
- Built-in materials are already **PBR** (physically based) since the 2020–2022 overhaul — they react
  correctly to lighting out of the box.

---

## 3. Custom materials — MaterialVariant + MaterialService

You're not limited to the 45. You can make your own with custom textures:

- **`MaterialVariant`** (an object) defines a custom material:
  - `BaseMaterial` — which built-in material it inherits physical/shader behavior from (e.g. Grass).
  - `ColorMap` / `NormalMap` / `MaterialPattern` / `Studs` etc. — your textures.
- **`MaterialService`** wires variants in:
  - **Global override:** `MaterialService` has a slot per built-in material
    (`MaterialService.Asphalt`, `.Grass`, …) — set it to a `MaterialVariant` and *every* part using
    that built-in material across the whole game switches to your texture. Great for a consistent art style.
  - **Per-part:** parent a `MaterialVariant` directly under a part, or assign via
    `MaterialService:SetBaseMaterialOverride` / `BasePart.MaterialVariant` to apply to just that part.
- Created in Studio via the **Material Manager** window, or fully by **script** (pi can spawn and
  configure `MaterialVariant` instances in Luau — perfect for bulk/automated setups).

**Rule of thumb:** use built-in materials for gameplay physics; use MaterialVariants when you want a
custom look while keeping that material's physics.

---

## 4. PBR SurfaceAppearance (for MeshParts / imported 3D)

For imported meshes (`MeshPart`), add a **`SurfaceAppearance`** child object with up to **5 PBR texture maps**:

| Map | What it does |
|---|---|
| **ColorMap** | Base color / albedo (the plain color + pattern) |
| **NormalMap** | Faked surface bumps/scratches without adding geometry |
| **RoughnessMap** | How glossy (white = rough/matte) vs shiny (black = mirror) |
| **MetalnessMap** | Which pixels are bare metal (white) vs dielectric (black) |
| **EmissiveMap** | (newer) self-glow, like Neon but per-pixel |

Get all four core maps from one texture set and Roblox lighting handles reflections/shading/depth
automatically. Note: most SurfaceAppearance properties can't be changed by script at runtime
(the engine pre-processes them).

---

## 5. Texture specs (so sources match Roblox)

- **Power-of-two, seamless/tileable** textures tile best (256², 512², 1024²; 2048²/4096² for hero assets).
- Roblox's built-in PBR materials use ~512²–1024² maps. Match that for performance.
- **File upload:** PNG (color/normal/roughness/metalness) and for some usages JPG. Keep each map
  seamless or you'll see seams when it tiles.
- The `ColorMap` should have **no baked lighting/shadows** (flat albedo) so Roblox lighting looks right.

---

## 6. Where to get free materials (all CC0 = legal for Roblox monetization, no attribution)

These are the safe, commercial-use, no-attribution libraries — pull PBR sets (color+normal+roughness+metalness):

| Source | URL | Notes |
|---|---|---|
| **Poly Haven** | polyhaven.com/textures | The gold standard; CC0; 4K/8K; consistent quality |
| **ambientCG** | ambientcg.com | 2000+ CC0 PBR materials; great coverage |
| **Mixos** | mixos.io/free-textures | Curated seamless CC0 sets |
| **FreePBR** | freepbr.com | 600+ free PBR (metalness/roughness workflow) |
| **Roblox Creator Store / Toolbox** | create.roblox.com/store | Free + paid **material packs** & MaterialVariants ready-to-use |

> ⚠️ Avoid Quixel Megascans and other licensed libraries for Roblox unless the license explicitly
> permits it — their terms can block commercial/external use. Stick to CC0.

**Convert → use:** download a CC0 set → (optionally resize to 1024², make seamless in Blender/GIMP/
ImageMagick) → upload as textures → drop into a `MaterialVariant` (parts) or `SurfaceAppearance` (mesh).

---

## 7. AI material generation (2026)

- **Roblox Studio built-in:** **Material/Texture Generator** creates textures from text prompts
  (runs inside Studio on the Windows host). **Assistant** can also generate simple textures.
- **PLAYTEX AI** (playtex.ai) — Roblox-specific: generate a texture then export color/normal/
  roughness/metalness maps ready for SurfaceAppearance/MaterialVariant.
- **General AI texture tools:** Polycam, PBR Generator, Texture Lab, etc. — output PBR sets you import.

---

## 8. What pi (WSL) can do with materials right now

- **Bulk-generate material assignments** in Luau — paint a whole procedural map (terrain, buildings)
  with the right built-in materials from code.
- **Create & configure `MaterialVariant` instances by script** — set BaseMaterial + map asset IDs
  programmatically, so a whole custom palette is one script away.
- **Download & prep CC0 texture packs** — fetch from Poly Haven/ambientCG, resize/tile with
  ImageMagick or Blender headless, stage the files.
- **Drive Blender headless** (once installed) to bake/seam textures and generate normal/roughness maps.
- **Upload via Open Cloud API** (with a key) to get asset IDs without touching Studio.
- **Re-skin an existing map** — run Lune/Remodel scripts over a `.rbxlx` to swap materials in bulk.

Needs you (Windows/Studio): first manual upload session, the in-Studio Material Manager for
real-time tweaking, and the built-in Texture Generator.

---

## 9. Quick recipe: CC0 texture → custom material (pi does 1–3, you do 4)

1. **Get a set** from Poly Haven/ambientCG (color + normal + roughness + metalness PNGs).
2. **pi:** resize to 1024², ensure seamless (ImageMagick/Blender).
3. **pi:** upload via Open Cloud → collect the 4 asset IDs.
4. **pi writes Luau** creating a `MaterialVariant` (BaseMaterial = closest match, e.g. `Rock`),
   assign the 4 IDs, and wire it into `MaterialService` as a global override or per-part.
5. Open in Studio → every matching surface now shows your custom material.

---

## Bottom line
- **45 built-in materials** cover most needs and are free + PBR + physically-correct.
- **Custom looks** = `MaterialVariant` (parts/terrain) or `SurfaceAppearance` (meshes) fed by PBR maps.
- **Free legal textures** = Poly Haven / ambientCG / Mixos / FreePBR (all CC0).
- **pi can own the whole pipeline** (download → process → upload → script into variants) except the
  in-Studio generator and first manual upload.
