"""Act I opening (Revan POV): Coruscant, the Dealer's Den.

Revan, restless and haunted by fragments of memory two years after the war,
meets Mandalore, who brings a lead that will start the hunt. Self-contained
walkable module (cantina geometry reused), built on the proven slice pattern.
All dialogue is original (paraphrasing the novel's beat, not its text).
Run: python slices/act1_coruscant.py   then  warp tor_coru
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import bif, rim, erfwrite, gfftool, tlk, dlgbuild
from gfftool import Struct, RESREF, LOCSTR, CEXOSTR, FLOAT

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override"); MODS = os.path.join(K2, "modules")
SRC_MODULE = "203TEL"; AREA = "tor_coru"
bif.GAME = K2; bifs, res = bif.load_key()

# original lines (my own writing; never the novel's text)
NPC = [
 "Don't tell me the famous Revan has forgotten the man behind the mask. It's Canderous. Canderous Ordo. We spilled blood together aboard the Star Forge, before duty made a stranger of you. Now sit. I didn't crawl into this corner of Coruscant for the atmosphere.",
 "Maybe. There are Mandalorian relics from the war that speak of an enemy your Republic never names. If those nightmares of yours have a face, it is buried out there in the cold.",
 "Because whatever hunts your sleep hunted my people first, at Malachor and long before it. I intend to learn what we truly died for.",
 "I thought you would say that. Gear up. The Ebon Hawk is fueled, and we begin where the war ended.",
]
PC = [
 "You said you found something. The dreams. The thing I can't remember.",
 "Then why come at all, Mandalore?",
 "Then we leave together. Tell me where.",
]

def get_or_append(texts):
    _, strings = tlk.read(os.path.join(K2, "dialog.tlk"))
    ex = {s["text"]: i for i, s in enumerate(strings)}
    return [ex[t] for t in texts] if all(t in ex for t in texts) else tlk.append(os.path.join(K2, "dialog.tlk"), texts)

refs = get_or_append(NPC + PC); nref, pref = refs[:4], refs[4:]

# DLG: E0 offers R0/R1/R2; R0->E1, R1->E2 (both then offer R2), R2->E3 (end)
E = [dlgbuild.entry(0, nref[0], [0, 1, 2]),
     dlgbuild.entry(1, nref[1], [2]),
     dlgbuild.entry(2, nref[2], [2]),
     dlgbuild.entry(3, nref[3], [])]
R = [dlgbuild.reply(pref[0], [1]), dlgbuild.reply(pref[1], [2]), dlgbuild.reply(pref[2], [3])]
dlgbuild.write_dlg(os.path.join(OVR, "tor_mand_dlg.dlg"), E, R, [0], vo_id="tor_mandalore")

# Mandalore NPC (clone p_mand for valid stats; appearance 462 = Party_NPC_Mandalore)
_, _, utc = gfftool.read(bif.extract("p_mand", 2027, bifs, res))
utc.fields["FirstName"] = (LOCSTR, (-1, [(0, "Mandalore")]))
utc.fields["Tag"] = (CEXOSTR, "tor_mandalore")
utc.fields["TemplateResRef"] = (RESREF, "tor_mandalore")
utc.fields["FactionID"] = (utc.fields["FactionID"][0], 5)
utc.fields["Conversation"] = (utc.fields.get("Conversation", (RESREF, ""))[0], "tor_mand_dlg")
gfftool.write(os.path.join(OVR, "tor_mandalore.utc"), "UTC ", "V3.2", utc)

# self-contained module clone (empty GIT + Mandalore at entry)
lyt = bif.extract(SRC_MODULE.lower(), 3000, bifs, res)
vis = bif.extract(SRC_MODULE.lower(), 3001, bifs, res)
ents = rim.read_rim(os.path.join(MODS, SRC_MODULE + ".rim"))
are_b = next(d for r, t, d in ents if t == 2012)
_, _, gt = gfftool.read(next(d for r, t, d in ents if t == 2023))
_, _, it = gfftool.read(next(d for r, t, d in ents if t == 2014))
ex, ey, ez = (it.fields[k][1] for k in ("Mod_Entry_X", "Mod_Entry_Y", "Mod_Entry_Z"))

proto = gt.fields["Creature List"][1][0]
for lab, (ft, v) in list(gt.fields.items()):
    if ft == 15: gt.fields[lab] = (ft, [])
man = Struct(proto.stype, dict(proto.fields))
man.fields["TemplateResRef"] = (RESREF, "tor_mandalore")
man.fields["XPosition"] = (FLOAT, ex); man.fields["YPosition"] = (FLOAT, ey - 3.0); man.fields["ZPosition"] = (FLOAT, ez)
man.fields["XOrientation"] = (FLOAT, 0.0); man.fields["YOrientation"] = (FLOAT, 1.0)
gt.fields["Creature List"] = (15, [man])

it.fields["Mod_Entry_Area"] = (RESREF, AREA); it.fields["Mod_Tag"] = (CEXOSTR, AREA)
it.fields["Mod_Area_list"][1][0].fields["Area_Name"] = (RESREF, AREA)

mod_files = [
    ("module", 2014, gfftool.write(None, "IFO ", "V3.2", it)),
    (AREA, 2012, are_b),
    (AREA, 2023, gfftool.write(None, "GIT ", "V3.2", gt)),
    (AREA, 3000, lyt), (AREA, 3001, vis),
    ("tor_mandalore", 2027, open(os.path.join(OVR, "tor_mandalore.utc"), "rb").read()),
    ("tor_mand_dlg", 2029, open(os.path.join(OVR, "tor_mand_dlg.dlg"), "rb").read()),
]
erfwrite.write(os.path.join(MODS, "tor_coru.mod"), mod_files, "MOD ")
print("built tor_coru.mod (Coruscant/Dealer's Den) with Mandalore. strrefs %s -> warp tor_coru" % refs)
