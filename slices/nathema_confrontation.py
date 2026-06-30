"""M1 vertical slice: the Nathema/Emperor confrontation.

Assembles a walkable TSL module (`tor_nath`) by fully cloning the Korriban
academy area under a unique area name, and injects a custom neutral
"Sith Emperor" NPC with an original branching conversation that can turn
into a fight. Run:  python slices/nathema_confrontation.py   then  warp tor_nath
"""
import os, sys, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import bif, rim, gfftool, tlk, dlgbuild
from gfftool import Struct, RESREF, LOCSTR, CEXOSTR, FLOAT
from pykotor.resource.formats.ncs import compile_nss, bytes_ncs
from pykotor.common.misc import Game

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override"); MODS = os.path.join(K2, "modules")
SRC_MODULE = "702KOR"          # area reused as the Nathema-temple stand-in
AREA = "tor_nath"
bif.GAME = K2; bifs, res = bif.load_key()

# original confrontation lines (my own writing; never the novel's text)
NPC = [
 "So the Republic's wandering hero comes at last to the edge of the galaxy. You have walked a long and ruinous road to stand before me, Revan.",
 "Memory is a fragile thing. I unmade yours once and set you loose as my instrument. I can unmake it again, and this time leave nothing of you behind.",
 "I am the hunger at the end of the stars, the empire that will outlast every republic that frightened men dare to build. You were always meant to kneel.",
 "Then there is nothing left to say. Fall, as all things before you have fallen.",
]
PC = [
 "I remember now. I know what you are, and the doom you would bring to the Republic.",
 "Who are you? Why do I feel as though I have stood against you before?",
 "Then I will end this here, as I should have long ago.",
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

# dialogue -> combat script
fight = 'void main(){ ChangeToStandardFaction(GetObjectByTag("tor_emperor"), STANDARD_FACTION_HOSTILE_1); }'
open(os.path.join(OVR, "tor_emp_fight.ncs"), "wb").write(bytes(bytes_ncs(compile_nss(fight, Game.K2))))

# DLG
E = [dlgbuild.entry(0, nref[0], [0, 1, 2]),
     dlgbuild.entry(1, nref[1], [2]),
     dlgbuild.entry(2, nref[2], [2]),
     dlgbuild.entry(3, nref[3], [], script="tor_emp_fight")]
R = [dlgbuild.reply(pref[0], [1]), dlgbuild.reply(pref[1], [2]), dlgbuild.reply(pref[2], [3])]
dlgbuild.write_dlg(os.path.join(OVR, "tor_emp_dlg.dlg"), E, R, [0], vo_id="tor_emperor")

# UTC: The Sith Emperor (neutral; talk first)
_, _, utc = gfftool.read(bif.extract("n_darthnihilus", 2027, bifs, res))
utc.fields["FirstName"] = (LOCSTR, (-1, [(0, "The Sith Emperor")]))
utc.fields["Tag"] = (CEXOSTR, "tor_emperor")
utc.fields["TemplateResRef"] = (RESREF, "tor_emperor")
utc.fields["FactionID"] = (utc.fields["FactionID"][0], 5)
utc.fields["Conversation"] = (utc.fields.get("Conversation", (RESREF, ""))[0], "tor_emp_dlg")
gfftool.write(os.path.join(OVR, "tor_emperor.utc"), "UTC ", "V3.2", utc)

# full module clone under a unique area name (avoids collision; ships geometry refs + templates)
lyt = bif.extract(SRC_MODULE.lower(), 3000, bifs, res)
vis = bif.extract(SRC_MODULE.lower(), 3001, bifs, res)
ents = rim.read_rim(os.path.join(MODS, SRC_MODULE + ".rim"))
are_b = next(d for r, t, d in ents if t == 2012)
_, _, gt = gfftool.read(next(d for r, t, d in ents if t == 2023))
_, _, it = gfftool.read(next(d for r, t, d in ents if t == 2014))

proto = gt.fields["Creature List"][1][0]
emp = Struct(proto.stype, dict(proto.fields))
emp.fields["TemplateResRef"] = (RESREF, "tor_emperor")
emp.fields["XPosition"] = (FLOAT, 121.6); emp.fields["YPosition"] = (FLOAT, 150.0); emp.fields["ZPosition"] = (FLOAT, 0.15)
emp.fields["XOrientation"] = (FLOAT, 0.0); emp.fields["YOrientation"] = (FLOAT, 1.0)
gt.fields["Creature List"] = (gt.fields["Creature List"][0], [emp])
gt.fields["TriggerList"] = (gt.fields["TriggerList"][0], [])     # strip area-transition triggers (load-loop fix)

it.fields["Mod_Entry_Area"] = (RESREF, AREA)
it.fields["Mod_Tag"] = (CEXOSTR, AREA)
it.fields["Mod_Area_list"][1][0].fields["Area_Name"] = (RESREF, AREA)

rim.write_rim(os.path.join(MODS, "tor_nath.rim"), [
    (AREA, 2012, are_b),
    (AREA, 2023, gfftool.write(None, "GIT ", "V3.2", gt)),
    ("module", 2014, gfftool.write(None, "IFO ", "V3.2", it)),
    (AREA, 3000, lyt),
    (AREA, 3001, vis),
])
shutil.copy(os.path.join(MODS, SRC_MODULE + "_s.rim"), os.path.join(MODS, "tor_nath_s.rim"))
print("built tor_nath (+_s) area '%s', dialogue strrefs %s -> warp tor_nath" % (AREA, refs))
