# Pipeline notes & item codes

## Model/item conventions (KOTOR 1)
- Weapon model long axis = **Z**; grip near `z=0`, blade/emitter toward **+Z**. Units ≈ meters.
- Lightsaber base item = `baseitems.2da` row **8** (`itemclass w_Lghtsbr`). The item's
  `ModelVariation = NNN` selects model `w_lghtsbr_<NNN>.mdl/.mdx`.
- `giveitem` uses the item's **resref** (the `.uti` filename), not its tag.
- `giveitem` silently no-ops (no console error) if the resref doesn't exist.

## Stock animated saber structure (template for kitbash)
`w_lghtsbr_001`:
```
w_Lghtsbr_001 (root)
└─ Dummy01
   └─ lshandle01        <- hilt mesh (replace this)
      ├─ plane239        \
      ├─ plane240         } blade planes
      ├─ plane241        /
      └─ plane242
```
Animations: `powered, off, powerup, powerdown, throwout, throwback`.
Kitbash = swap `lshandle01`'s mesh data only; keep blade children + animations + transforms.

## KotorBlender export gotchas (Blender 5.1)
- Objects must use **quaternion** rotation mode (`obj.rotation_mode='QUATERNION'`) or export errors.
- Mesh node texture comes from `obj.kb.bitmap`; set `obj.kb.meshtype='TRIMESH'`.
- Animated import/export requires the `patches/` fixes (channelbag API).

## Current test artifact (regenerate with blender/kitbash_saber.py)
- Model: `w_lghtsbr_099.mdl/.mdx` (custom hilt + stock blade/animations)
- Item:  `g_w_hilt99sbr.uti` (Lightsaber, ModelVariation=99)
- Spawn in-game: `giveitem g_w_hilt99sbr`

## Also installed in this KOTOR (not part of this repo)
- Door-opener armband (whereami-derived): `giveitem d3_location`
