# TOR_Revan

A Star Wars: Knights of the Old Republic (KOTOR 1) mod project, inspired by the events of the
*Star Wars: The Old Republic — Revan* novel.

This repository holds the **source and tooling** for the mod — the Python utilities, Blender
asset-generation scripts, and engine/tooling patches. It deliberately does **not** contain
extracted BioWare/LucasArts game assets or game-derived binaries (see `.gitignore`); those are
regenerated locally from the scripts here.

## Layout

| Path | Contents |
|------|----------|
| `tools/` | Pure-Python readers/writers for KOTOR file formats (no game assets) |
| `blender/` | Headless Blender (`bpy`) scripts that generate/kitbash models |
| `patches/` | Patches to third-party tools (KotorBlender) needed for the pipeline |
| `renders/` | Preview renders of generated assets |
| `docs/` | Pipeline notes and in-game item codes |

### `tools/` — KOTOR format library (original work)
- `twoda.py` — read/write binary `2DA V2.b` tables (verified byte-faithful round-trip).
- `gff.py` — read GFF files (UTI/UTC/UTD/ARE/…); field/label/struct parsing.
- `bif.py` — parse `chitin.key` + BIF archives; extract resources by ResRef/type.
- `erf.py` — read ERF/MOD/RIM archives (modules).

### `blender/` — asset generation
- `hilt_v1.py`, `hilt_v2.py` — parametric lightsaber-hilt generator + studio render
  (the VLM-in-the-loop iteration: v1 critiqued visually → v2 fixes).
- `inspect_saber.py` — import a model and dump its node hierarchy.
- `build_saber_model.py` — export a static hilt-only weapon model.
- `kitbash_saber.py` — **main**: swap the generated hilt onto the stock animated saber,
  preserving the blade + ignition animations, and export a new model variation.

## Pipeline

1. Generate hilt geometry procedurally in Blender (`blender/hilt_v2.py`).
2. Import the stock animated lightsaber via KotorBlender (requires the patch below).
3. Replace the stock hilt mesh with the generated one, keeping blade + animations
   (`blender/kitbash_saber.py`).
4. Export to `w_lghtsbr_<NNN>.mdl/.mdx`; create a lightsaber `.uti` with `ModelVariation=NNN`.
5. `giveitem` in-game to test.

### Requirements
- Blender 5.1 (headless: `blender --background --python <script>`)
- [KotorBlender](https://github.com/seedhartha/kotorblender) 4.0.3 — **with** the patches in
  `patches/` applied (see below).
- A local KOTOR 1 installation (for extracting stock models/textures via `tools/bif.py`).

### KotorBlender on Blender 5.1
KotorBlender 4.0.3 targets Blender 3.6. On Blender 4.4+ the animation system changed
(slotted/layered actions), and `Action.fcurves` was removed, which crashes import/export of
**animated** models. The patches in `patches/` route fcurve access through the new per-slot
**channelbag** API, restoring animated import/export. Apply with:

```
cd <kotorblender>/io_scene_kotor/scene
patch -p1 < /path/to/patches/kotorblender_b51_animnode.patch
patch -p1 < /path/to/patches/kotorblender_b51_armature.patch
```

## Status
- ✅ KOTOR format tooling (2DA/GFF/BIF/ERF)
- ✅ Parametric hilt generator + render loop
- ✅ KotorBlender patched for Blender 5.1 (animated import/export works)
- ✅ Custom hilt kitbashed onto animated saber (blade + ignition preserved), in-game via `giveitem`
- ⬜ Custom blade texture / UVs
- ⬜ Revan-novel content (areas, characters, quests, items)

See `docs/` for details and item codes.
