"""Wire the Act I modules into a connected, playable flow with a journal quest.

Flow:  tor_coru (Dealer's Den, meet Mandalore)
         --[dialogue end: k_tor_leave1]--> tor_hawk (Ebon Hawk hub)
         --[set course: k_tor_leave2]--> tor_nath (the dead world / confrontation)

Journal quest "tor_hunt" updates at each step (10 -> 20 -> 30 on the confrontation).
All dialogue is original writing.
"""
import os, sys, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import bif, rim, erf, erfwrite, gfftool, tlk, dlgbuild, journal, populate
from gfftool import Struct, RESREF, LOCSTR, CEXOSTR, FLOAT
from pykotor.resource.formats.ncs import compile_nss, bytes_ncs
from pykotor.common.misc import Game

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override"); MODS = os.path.join(K2, "modules")
bif.GAME = K2; bifs, res = bif.load_key()

def comp(src):  # compile NSS -> NCS bytes
    return bytes(bytes_ncs(compile_nss(src, Game.K2)))

# 1) journal quest
journal.append_quest(K2, "tor_hunt", "The Hunt", [
    (10, "Mandalore - Canderous Ordo - brought word of Mandalorian relics that may explain the visions haunting me. We set course aboard the Ebon Hawk.", False),
    (20, "The trail has led to a dead world at the edge of the galaxy, drained of all life and the Force. Something ancient waits there.", False),
    (30, "I faced the darkness at the heart of the dead world. The hunt is far from over.", True),
])

# 2) transition scripts.
# NOTE: the Ebon Hawk (003EBO) is special-cased in KOTOR and does not load as a
# standalone cloned module, so we route Coruscant straight to the dead world.
open(os.path.join(OVR, "k_tor_leave1.ncs"), "wb").write(comp(
    'void main(){ AddJournalQuestEntry("tor_hunt", 10); AddJournalQuestEntry("tor_hunt", 20); StartNewModule("tor_nath"); }'))
open(os.path.join(OVR, "k_tor_leave2.ncs"), "wb").write(comp(
    'void main(){ AddJournalQuestEntry("tor_hunt", 20); StartNewModule("tor_nath"); }'))
# confrontation script now also advances the journal to complete
open(os.path.join(OVR, "tor_emp_fight.ncs"), "wb").write(comp(
    'void main(){ ChangeToStandardFaction(GetObjectByTag("tor_emperor"), STANDARD_FACTION_HOSTILE_1); AddJournalQuestEntry("tor_hunt", 30); }'))

# 3) Ebon Hawk hub dialogue (Mandalore sets course)
HAWK_NPC = ["The Hawk is yours to command, Revan. Say the word and we burn for whatever it is that haunts you."]
HAWK_PC = ["Set course. Take us to the coordinates drawn from the relics."]
HAWK_END = ["Then strap in. Whatever waits out there has waited a very long time for you."]
_, strings = tlk.read(os.path.join(K2, "dialog.tlk"))
ex = {s["text"]: i for i, s in enumerate(strings)}
allh = HAWK_NPC + HAWK_PC + HAWK_END
hrefs = [ex[t] for t in allh] if all(t in ex for t in allh) else tlk.append(os.path.join(K2, "dialog.tlk"), allh)
HE = [dlgbuild.entry(0, hrefs[0], [0]),
      dlgbuild.entry(1, hrefs[2], [])]
HR = [dlgbuild.reply(hrefs[1], [1])]
dlgbuild.write_dlg(os.path.join(OVR, "tor_hawkdlg.dlg"), HE, HR, [0], vo_id="tor_mandalore", end_script="k_tor_leave2")

# 4) Ebon Hawk hub module (clone 003EBO; Mandalore as navigator)
SRC = "003EBO"
ents = rim.read_rim(os.path.join(MODS, SRC + ".rim"))
src_area = next(r for r, t, d in ents if t == 2012)          # the area's real resref
are_b = next(d for r, t, d in ents if t == 2012)
_, _, gt = gfftool.read(next(d for r, t, d in ents if t == 2023))
_, _, it = gfftool.read(next(d for r, t, d in ents if t == 2014))
lyt = bif.extract(src_area, 3000, bifs, res); vis = bif.extract(src_area, 3001, bifs, res)
AREA = "tor_hawk"
ex_, ey_, ez_ = (it.fields[k][1] for k in ("Mod_Entry_X", "Mod_Entry_Y", "Mod_Entry_Z"))

# Mandalore navigator UTC (talk to set course)
_, _, man = gfftool.read(bif.extract("p_mand", 2027, bifs, res))
man.fields["FirstName"] = (LOCSTR, (-1, [(0, "Mandalore")]))
man.fields["Tag"] = (CEXOSTR, "tor_man_hawk")
man.fields["TemplateResRef"] = (RESREF, "tor_man_hawk")
man.fields["FactionID"] = (man.fields["FactionID"][0], 5)
man.fields["Conversation"] = (man.fields.get("Conversation", (RESREF, ""))[0], "tor_hawkdlg")
gfftool.write(os.path.join(OVR, "tor_man_hawk.utc"), "UTC ", "V3.2", man)

proto = gt.fields["Creature List"][1][0]
for lab, (ft, v) in list(gt.fields.items()):
    if ft == 15: gt.fields[lab] = (ft, [])
nav = Struct(proto.stype, dict(proto.fields))
nav.fields["TemplateResRef"] = (RESREF, "tor_man_hawk")
nav.fields["XPosition"] = (FLOAT, ex_); nav.fields["YPosition"] = (FLOAT, ey_ - 3.0); nav.fields["ZPosition"] = (FLOAT, ez_)
nav.fields["XOrientation"] = (FLOAT, 0.0); nav.fields["YOrientation"] = (FLOAT, 1.0)
gt.fields["Creature List"] = (15, [nav])

# ambient Ebon Hawk crew (neutral, mute). Verified appearance.2da rows:
# 57 Droid_Astro_01 (utility droid), 191 Commoner_Mal_Black_01_A (generic crew).
AMBIENT_HAWK = [
    ("tor_hawk_amb1", "Utility Droid", 57),   # astromech / utility droid
    ("tor_hawk_amb2", "Crew Hand",    191),   # generic human crew member
]
HAWK_OFFS = [(2.0, 1.5), (-2.0, 1.5)]
amb_files = []
for (rr, nm, ap), (dx, dy) in zip(AMBIENT_HAWK, HAWK_OFFS):
    populate.ambient_utc(rr, nm, ap, bifs, res, OVR)
    populate.append_creature(gt, proto, rr, ex_ + dx, ey_ + dy, ez_, -dx, -dy)
    amb_files.append((rr, 2027, open(os.path.join(OVR, rr + ".utc"), "rb").read()))

it.fields["Mod_Entry_Area"] = (RESREF, AREA); it.fields["Mod_Tag"] = (CEXOSTR, AREA)
it.fields["Mod_Area_list"][1][0].fields["Area_Name"] = (RESREF, AREA)
erfwrite.write(os.path.join(MODS, "tor_hawk.mod"), [
    ("module", 2014, gfftool.write(None, "IFO ", "V3.2", it)),
    (AREA, 2012, are_b),
    (AREA, 2023, gfftool.write(None, "GIT ", "V3.2", gt)),
    (AREA, 3000, lyt), (AREA, 3001, vis),
    ("tor_man_hawk", 2027, open(os.path.join(OVR, "tor_man_hawk.utc"), "rb").read()),
    ("tor_hawkdlg", 2029, open(os.path.join(OVR, "tor_hawkdlg.dlg"), "rb").read()),
] + amb_files, "MOD ")

# 5) rebuild Coruscant so Mandalore's last line fires k_tor_leave1
subprocess.run([sys.executable, os.path.join(ROOT, "slices", "act1_coruscant.py")], check=True)

print("flow wired: warp tor_coru -> (talk to Mandalore, end convo) -> tor_nath; quest 'The Hunt' tracks it. (Ebon Hawk hub deferred - 003EBO won't load standalone.)")
