"""Act I intro: Lord Scourge reports to Darth Nyriss on Dromund Kaas.

Assembles a walkable, self-contained TSL module (`tor_kaas`) by cloning the
851NIH Sith-stronghold area under a unique area name, and injects a custom
neutral "Darth Nyriss" NPC with an original branching conversation that
evokes the Ch.1 beat (Scourge returns to Dromund Kaas, his Sith master tests
his loyalty and hints at a hidden threat on the Dark Council).

Mirrors the proven slices/nathema_confrontation.py pattern exactly.
Run:  python slices/scourge_intro.py    then  warp tor_kaas
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import bif, rim, gfftool, tlk, dlgbuild, erfwrite
from gfftool import Struct, RESREF, LOCSTR, CEXOSTR, FLOAT, WORD

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override"); MODS = os.path.join(K2, "modules")
SRC_MODULE = "851NIH"          # Dromund Kaas / Sith-stronghold stand-in
SRC_AREA = "851nih"            # original area resref (BIF geometry + RIM are/git)
AREA = "tor_kaas"
bif.GAME = K2; bifs, res = bif.load_key()

# --- original conversation lines (my own writing; never the novel's text) ---
NPC = [
 "Scourge. So my newest blade finds his way back to Dromund Kaas at last. Kneel, and give me one reason I should not strip the insolence from your bones.",
 "Loyalty. Every wretch who crawls the floors of this Council swears it to my face, then sharpens a knife for my back. Words are cheap on Dromund Kaas. Show me you are worth the air you waste.",
 "Then hear the truth few on the Dark Council dare to whisper: there is a rot among us, an enemy who wears the smile of a trusted ally. I have laid a trap, and you, my unproven servant, will be the blade that springs it.",
 "Serve me well, and you will climb higher than your meager birth could ever dream. Fail me, and not even the Force will find what is left of you. Now go - and watch the shadows as closely as you watch your enemies.",
]
PC = [
 "I serve the Empire, my lord, and through the Empire I serve you. My loyalty has never been in question.",
 "I have crossed half the galaxy to lay this news at your feet. Hear me before you waste your threats.",
 "Then test me. I have spilled more blood for the Empire than your perfumed courtiers ever will.",
 "Name the traitor, and I will lay their head before your throne.",
 "A trap is only as strong as its bait. What is it you are not telling me, my lord?",
]

def get_or_append_strrefs(texts):
    """Idempotent: reuse existing StrRefs if already present, else append."""
    _, strings = tlk.read(os.path.join(K2, "dialog.tlk"))
    existing = {s["text"]: i for i, s in enumerate(strings)}
    if all(t in existing for t in texts):
        return [existing[t] for t in texts]
    return tlk.append(os.path.join(K2, "dialog.tlk"), texts)

refs = get_or_append_strrefs(NPC + PC)
nref, pref = refs[:4], refs[4:]

# --- DLG: branching tree (4 NPC entries, 5 player replies) ---
# E0 -> R0("loyalty")->E1, R1("hear me")->E2
# E1 -> R2("test me")->E2
# E2 -> R3("name the traitor")->E3, R4("what aren't you telling me")->E3
# E3 -> end
E = [dlgbuild.entry(0, nref[0], [0, 1]),
     dlgbuild.entry(1, nref[1], [2]),
     dlgbuild.entry(2, nref[2], [3, 4]),
     dlgbuild.entry(3, nref[3], [])]
R = [dlgbuild.reply(pref[0], [1]),
     dlgbuild.reply(pref[1], [2]),
     dlgbuild.reply(pref[2], [2]),
     dlgbuild.reply(pref[3], [3]),
     dlgbuild.reply(pref[4], [3])]
dlgbuild.write_dlg(os.path.join(OVR, "tor_nyr_dlg.dlg"), E, R, [0], vo_id="tor_nyriss")

# --- UTC: Darth Nyriss (clone a valid dark-jedi template; neutral so talkable) ---
_, _, utc = gfftool.read(bif.extract("n_darthtraya", 2027, bifs, res))
utc.fields["FirstName"] = (LOCSTR, (-1, [(0, "Darth Nyriss")]))
utc.fields["Tag"] = (CEXOSTR, "tor_nyriss")
utc.fields["TemplateResRef"] = (RESREF, "tor_nyriss")
utc.fields["FactionID"] = (utc.fields["FactionID"][0], 5)            # 5 = Neutral
utc.fields["Appearance_Type"] = (utc.fields["Appearance_Type"][0], 421)  # Dark_Jedi_Master_02 (robed F)
utc.fields["Conversation"] = (utc.fields.get("Conversation", (RESREF, ""))[0], "tor_nyr_dlg")
gfftool.write(os.path.join(OVR, "tor_nyriss.utc"), "UTC ", "V3.2", utc)

# --- self-contained module (single .mod): reuse area geometry from BIF,
#     empty every GIT object list (no external templates), inject Nyriss. ---
lyt = bif.extract(SRC_AREA, 3000, bifs, res)
vis = bif.extract(SRC_AREA, 3001, bifs, res)
ents = rim.read_rim(os.path.join(MODS, SRC_MODULE + ".rim"))
are_b = next(d for r, t, d in ents if t == 2012)
_, _, gt = gfftool.read(next(d for r, t, d in ents if t == 2023))
_, _, it = gfftool.read(next(d for r, t, d in ents if t == 2014))

proto = gt.fields["Creature List"][1][0]
for lab, (ft, v) in list(gt.fields.items()):
    if ft == 15:
        gt.fields[lab] = (ft, [])                 # empty all object lists (no template deps)

# place Nyriss a few units in front of the entry point, facing back toward the player
ex = it.fields["Mod_Entry_X"][1]; ey = it.fields["Mod_Entry_Y"][1]; ez = it.fields["Mod_Entry_Z"][1]
dx = it.fields["Mod_Entry_Dir_X"][1]; dy = it.fields["Mod_Entry_Dir_Y"][1]
nyr = Struct(proto.stype, dict(proto.fields))
nyr.fields["TemplateResRef"] = (RESREF, "tor_nyriss")
nyr.fields["XPosition"] = (FLOAT, ex + dx * 3.0)
nyr.fields["YPosition"] = (FLOAT, ey + dy * 3.0)
nyr.fields["ZPosition"] = (FLOAT, ez)
nyr.fields["XOrientation"] = (FLOAT, -dx)         # face back toward the entry/player
nyr.fields["YOrientation"] = (FLOAT, -dy)
gt.fields["Creature List"] = (15, [nyr])

it.fields["Mod_Entry_Area"] = (RESREF, AREA)
it.fields["Mod_Tag"] = (CEXOSTR, AREA)
it.fields["Mod_Area_list"][1][0].fields["Area_Name"] = (RESREF, AREA)

mod_files = [
    ("module", 2014, gfftool.write(None, "IFO ", "V3.2", it)),
    (AREA, 2012, are_b),
    (AREA, 2023, gfftool.write(None, "GIT ", "V3.2", gt)),
    (AREA, 3000, lyt),
    (AREA, 3001, vis),
]
for rr, rt, ext in [("tor_nyriss", 2027, ".utc"), ("tor_nyr_dlg", 2029, ".dlg")]:
    mod_files.append((rr, rt, open(os.path.join(OVR, rr + ext), "rb").read()))
erfwrite.write(os.path.join(MODS, "tor_kaas.mod"), mod_files, "MOD ")
print("built tor_kaas.mod (self-contained) area '%s', NPC tor_nyriss, dialogue strrefs %s" % (AREA, refs))
print("placement: (%.3f, %.3f, %.3f)" % (ex + dx*3.0, ey + dy*3.0, ez))
print("warp tor_kaas")
