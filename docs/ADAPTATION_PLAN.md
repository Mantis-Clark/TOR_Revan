# TOR_Revan — Full Adaptation Plan

Adaptation of *Star Wars: The Old Republic — Revan* (Drew Karpyshyn, 2011) as a KOTOR mod.
Structure below is derived directly from the novel: **Prologue + 31 chapters + Epilogue**, told
through two interleaved POVs (Revan; Lord Scourge) that converge when Meetra Surik enters (Ch. 17).

> ## Decisions locked (2026-06-30)
> - **Engine: KOTOR 2 / TSL.** Lore-natural (Meetra Surik = the K2 Exile; ending → SWTOR Maelstrom
>   Prison); native Exile/Mandalore/influence systems. TSL is installed at
>   `C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II` (Steam/Aspyr).
> - **POV: full 3-protagonist switching** (Revan / Lord Scourge / Meetra Surik).
> - **Scope: the complete 31-chapter adaptation** (both POVs, all acts).
>
> This is the most faithful and most ambitious configuration. See §7.5 for the K1→K2 port and §8 for
> how "full scope" is sequenced so it stays testable.

---

## 1. Scope & faithfulness

- **Goal:** a story-faithful, playable adaptation — the novel's plot, locations, and cast as KOTOR
  modules, quests, dialogue, and combat.
- **Estimated scale:** ~15 new areas, ~40+ speaking NPCs, 5 acts. This is BoS:SR-class or larger —
  a long project. The roadmap (§8) is built so each milestone is independently shippable/testable.
- **Distribution/legal:** ship as a *mod* (source + installer). Never redistribute BioWare assets or
  the novel text. Generated game-derived binaries stay local (see repo `.gitignore`).

---

## 2. Narrative architecture: how to play three POVs

The novel has three protagonists. KOTOR has one PC + party. Recommended approach:

**Act-scoped protagonist control** (the proven KOTOR 2 prologue technique — player controls T3, then
Atton, etc.). The single PC slot is reassigned per act via module-entry scripts that set appearance,
name, equipment, and party:
- **Revan** for Acts I–III (his investigation).
- **Lord Scourge** for the Sith-intrigue interludes (playable Sith on Dromund Kaas).
- **Meetra Surik** for Act IV (the rescue), then the party converges for Act V.

Alternative (simpler): play **only Revan**; render Scourge/Meetra chapters as cutscenes or party
members. Less faithful to the book's structure but far less work. **Decision in §9.**

---

## 3. Act & module breakdown (mapped to chapters)

| Act | Chapters | Module(s) | POV | Core gameplay |
|----|----------|-----------|-----|----------------|
| **I — Ghosts of the Past** | Prologue, 1–7 | Lehon Dream; Coruscant (Market, Jedi Temple, Dealer's Den); Ebon Hawk; Dromund Kaas (Kaas City); Hallion | Revan / Scourge | Tutorial dream; Revan's restless civilian life & recruiting Canderous; intro Sith Empire & Scourge's first mission |
| **II — The Trail to Rekkiad** | 8–14 | Rekkiad (glacier camp; Twin Spears tomb); Bosthirda (cave); Dromund Kaas | Revan / Scourge | Mandalorian clan conflict (Ordo vs Jendri); find the dead Sith & the clue to Nathema; Scourge uncovers Nyriss's conspiracy |
| **III — Nathema** | 15–18 | Nathema (surface ruins; temple interior); Coruscant (Bastila); Ebon Hawk | Revan → Scourge → Meetra | Revan reaches the dead world, confronts the Emperor, is **captured**; Bastila/Meetra begin the search |
| **IV — The Captive** | 19–24 | Dromund Kaas (Kaas City; Nyriss's Stronghold; Underground Prison) | Meetra / Scourge | Infiltrate as Scourge's "slave"; Scourge allies with the Jedi; free Revan; Nyriss/Sechel arc resolves |
| **V — The Emperor's Wrath** | 25–31, Epilogue | Dromund Kaas (Citadel assault; Throne/Ritual chamber) | Party | Citadel battle; duel with the Emperor; Scourge's vision & betrayal; Meetra falls; Revan re-imprisoned; epilogue hook to SWTOR |

**Module list (15):**
1. `tor_dream` — Lehon ruins (prologue dream). Reuse Lehon/Unknown World temple assets.
2. `tor_coru_mkt` — Coruscant Galactic Market (reuse Taris upper-city kit).
3. `tor_coru_tmpl` — Jedi Temple.
4. `tor_coru_den` — Dealer's Den cantina (reuse cantina kit).
5. `ebo_hawk` — Ebon Hawk hub (vanilla, re-dressed).
6. `tor_kaas_city` — Kaas City streets (rain; reuse Taris/Manaan exteriors).
7. `tor_nyriss` — Nyriss's stronghold (reuse Sith base/Dxun interiors).
8. `tor_citadel` — Emperor's citadel + throne/ritual chamber.
9. `tor_prison` — underground holding cells.
10. `tor_hallion` — Scourge's first mission world.
11. `tor_bosthirda` — meeting cave.
12. `tor_rekkiad1` — glacier surface / Mandalorian camp (reuse snow/cave).
13. `tor_rekkiad2` — Twin Spears tomb interior.
14. `tor_nathema1` — Nathema surface ruins (Force-dead, desaturated).
15. `tor_nathema2` — Nathema temple interior.

---

## 4. Cast (UTCs) & build approach

Build = reuse/kitbash existing heads+bodies + `appearance.2da` rows + texture recolors (we cannot
sculpt original faces).

**Party / protagonists:** Revan (existing Revan appearance + our custom hilt), Bastila, T3-M4
(vanilla), Canderous/Mandalore (reuse + Mandalore mask), Meetra Surik (reuse a female Jedi head),
Lord Scourge (red Sith Pureblood — reuse/recolor an alien head; this is the trickiest custom).

**Antagonists:** The Sith Emperor / Vitiate (final boss — robed humanoid + custom VFX), Darth Nyriss
(Dark Council), Sechel (spy), Darth Xedrix, Murtog (guard captain).

**Supporting:** Mandalorian clan NPCs (Ordo/Jendri), Jedi Council members, Coruscant civilians,
Sith guards/soldiers, prison guards, the Emperor's Guard (elite).

~40+ speaking roles; most are reskins of existing creature appearances.

---

## 5. Items & equipment

- **Player gear:** Revan's robes & mask (vanilla exist), **custom lightsaber hilt (DONE — pipeline
  proven)**, Scourge's saber, Meetra's saber, Mandalore's Mask & armor (BoS already has variants).
- **Quest items:** the Mandalorian clue/holocron from Rekkiad, Sith access cards, Nathema artifact.
- **Rewards:** unique sabers/crystals/armor per act.
- All items are `.uti` generated by our tooling; weapon models via the Blender kitbash pipeline.

---

## 6. Capability map (what *we* can build vs. what needs others)

| Component | Us (this toolchain) | Needs artist/VO/external |
|-----------|---------------------|--------------------------|
| Story, quest design, all dialogue trees | ✅ | |
| Scripts (NWScript) | ✅ source; needs a K1 NSS compiler in the loop | |
| Items, 2DA edits, journal, TLK strings | ✅ | |
| Module assembly (.are/.git/.ifo/.mod) | ✅ (needs GFF/ERF *writers* — see §7) | |
| Weapon/prop models | ✅ (Blender kitbash, proven) | |
| Characters | ✅ reskin/kitbash existing | Original faces → artist |
| Areas | ✅ re-dress existing room models | Original geometry → artist |
| Textures / icons | partial (recolor/composite) | Original art → artist / gen-AI |
| Voice acting | placeholder TTS only | Pro VO → cast/community |
| Cinematics | scripted in-engine | Pre-rendered → artist |

---

## 7. Technical foundation to build first (extends `tools/`)

Current `tools/` reads formats; the mod needs **writers** and a script compiler:
1. **GFF writer** — emit UTI/UTC/UTD/UTP/DLG/ARE/GIT/IFO/JRL (generalizes our readers).
2. **ERF/MOD writer** — pack modules into `.mod`.
3. **TLK appender** — add localized strings to `dialog.tlk` safely.
4. **NCS compiler integration** — wrap `nwnnsscomp` (K1 mode) so `.nss` → `.ncs` in the build.
5. **Build system** — one command: generate all GFFs → compile scripts → pack modules → emit a
   TSLPatcher installer (non-destructive 2DA/TLK merges, like the door-mod merge we did).
6. **Protagonist-switch + plot-state framework** — module-entry scripts + global vars (`globalcat`).

These are all squarely in scope for this toolchain (same binary-format work as 2DA/GFF/BIF/ERF).

---

## 7.5 KOTOR 1 → KOTOR 2 (TSL) port

What we built carries over; what changes is data schemas and a few engine specifics.

**Carries over unchanged:**
- `tools/` readers — TSL uses the same `KEY V1`, GFF, `2DA V2.b`, and ERF/MOD formats (verified:
  TSL `chitin.key` is `KEY V1`). `bif.py`/`erf.py`/`twoda.py`/`gff.py` work as-is.
- Blender pipeline — KotorBlender imports/exports TSL models; our Blender-5.1 fcurve patch is
  engine-agnostic. Saber kitbash method is identical (rebuild on TSL's saber model).

**Changes to handle:**
- **2DA schemas differ** (TSL `baseitems`, `spells`, `appearance`, `itempropdef`, `feat` have extra
  columns/rows). Our code is schema-agnostic for reading; the build's table edits must target TSL rows.
- **New restypes / fields** in TSL (e.g., extra GFF fields on UTC for influence). Writers must emit
  TSL-flavored templates.
- **Point at the TSL install** for all extraction/build/test.
- **Rebuild the custom saber** on TSL (the K1 `w_lghtsbr_099` artifact stays a K1 proof-of-concept).

**TSL features we now get for free (use them):**
- **Native prologue-style POV switching** — TSL ships with the Telos prologue (control T3, then the
  Exile). That exact mechanism is our 3-POV framework; we mirror it for Revan/Scourge/Meetra.
- **Influence system** for party (Bastila, Canderous, Meetra, Scourge dynamics).
- Better scripting hooks and the TSLPatcher ecosystem is TSL-first.

---

## 8. Phased roadmap

- **M0 — Foundation:** the §7 writers, compiler integration, build/installer. *Deliverable: build a
  trivial test module from source and load it in-game.*
- **M1 — Vertical slice (recommended: `tor_nathema2`, the Emperor confrontation):** one module fully
  playable — custom Revan, the custom saber, dialogue, a quest, the Emperor encounter, transitions in
  & out. Proves the *content* pipeline end-to-end. *This is the go/no-go milestone.*
- **M2 — Act I**, **M3 — Act II**, **M4 — Act III**, **M5 — Act IV**, **M6 — Act V** (each act =
  its modules + quests + cast, shippable as a chapter release).
- **M7 — Integration & balance:** full playthrough, pacing, save/transition hardening, installer.
- **Polish:** textures, VO (community/TTS), cinematics, music cues.

---

## 9. Decisions

1. **Engine:** ✅ **KOTOR 2 / TSL** (locked 2026-06-30).
2. **Protagonist model:** ✅ **Full 3-POV switching** (locked). Build order: Revan's path first, then
   wire Scourge and Meetra control via the TSL prologue mechanism (§7.5).
3. **Scope:** ✅ **Full 31-chapter adaptation** (locked). Sequenced act-by-act (§8) so each release is
   testable; "full" is the commitment, not a single monolithic drop.
4. **Art/VO sourcing:** ⬜ still open — solo (reuse-only + TTS placeholder) vs. recruit artists/voice
   actors. Not blocking M0/M1; decide before M2.

---

## 10. Immediate next steps
1. Lock §9 decisions.
2. Build M0 foundation (GFF writer first).
3. Stand up the M1 vertical slice and playtest in-game.
