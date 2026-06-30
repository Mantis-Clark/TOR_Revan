import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import os, rim, gfftool, bif, tlk, dlgbuild
from gfftool import Struct, RESREF, LOCSTR, CEXOSTR, FLOAT
from pykotor.resource.formats.ncs import compile_nss, bytes_ncs
from pykotor.common.misc import Game

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override"); MODS = os.path.join(K2, "modules")
bif.GAME = K2; bifs, res = bif.load_key()

# --- 1. original confrontation lines (my own writing, not the novel's text) ---
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
refs = tlk.append(os.path.join(K2, "dialog.tlk"), NPC + PC)
nref = refs[:4]; pref = refs[4:]

# --- 2. dialogue->combat script ---
fight_src = '''
void main() {
    object oEmp = GetObjectByTag("tor_emperor");
    ChangeToStandardFaction(oEmp, STANDARD_FACTION_HOSTILE_1);
}
'''
open(os.path.join(OVR, "tor_emp_fight.ncs"), "wb").write(bytes(bytes_ncs(compile_nss(fight_src, Game.K2))))

# --- 3. build the DLG ---
E = [
  dlgbuild.entry(0, nref[0], [0, 1, 2]),
  dlgbuild.entry(1, nref[1], [2]),
  dlgbuild.entry(2, nref[2], [2]),
  dlgbuild.entry(3, nref[3], [], script="tor_emp_fight"),
]
R = [
  dlgbuild.reply(pref[0], [1]),
  dlgbuild.reply(pref[1], [2]),
  dlgbuild.reply(pref[2], [3]),
]
dlgbuild.write_dlg(os.path.join(OVR, "tor_emp_dlg.dlg"), E, R, [0], vo_id="tor_emperor")

# --- 4. UTC with the conversation hooked up ---
_, _, utc = gfftool.read(bif.extract("n_darthnihilus", 2027, bifs, res))
utc.fields["FirstName"] = (LOCSTR, (-1, [(0, "The Sith Emperor")]))
utc.fields["Tag"] = (CEXOSTR, "tor_emperor")
utc.fields["TemplateResRef"] = (RESREF, "tor_emperor")
utc.fields["FactionID"] = (utc.fields["FactionID"][0], 5)       # Neutral (talk first)
ct = utc.fields.get("Conversation", (RESREF, ""))[0]
utc.fields["Conversation"] = (ct, "tor_emp_dlg")
gfftool.write(os.path.join(OVR, "tor_emperor.utc"), "UTC ", "V3.2", utc)

# --- 5. (re)assemble the walkable module with the Emperor at the entry ---
ents = rim.read_rim(os.path.join(MODS, "702KOR.rim"))
are_b = next(d for r,t,d in ents if t==2012)
_,_,gt = gfftool.read(next(d for r,t,d in ents if t==2023))
_,_,it = gfftool.read(next(d for r,t,d in ents if t==2014))
proto = gt.fields["Creature List"][1][0]
emp = Struct(proto.stype, dict(proto.fields))
emp.fields["TemplateResRef"] = (RESREF, "tor_emperor")
emp.fields["XPosition"] = (FLOAT, 121.6); emp.fields["YPosition"] = (FLOAT, 150.0)
emp.fields["ZPosition"] = (FLOAT, 0.15)
emp.fields["XOrientation"] = (FLOAT, 0.0); emp.fields["YOrientation"] = (FLOAT, 1.0)
gt.fields["Creature List"] = (gt.fields["Creature List"][0], [emp])
gt.fields["TriggerList"] = (gt.fields["TriggerList"][0], [])   # strip inherited area transitions (caused load loop)
it.fields["Mod_Tag"] = (CEXOSTR, "tor_nath")
rim.write_rim(os.path.join(MODS, "tor_nath.rim"), [
    ("702kor", 2012, are_b),
    ("702kor", 2023, gfftool.write(None, "GIT ", "V3.2", gt)),
    ("module", 2014, gfftool.write(None, "IFO ", "V3.2", it)),
])

# --- verify ---
_,_,dlg = gfftool.read(open(os.path.join(OVR,"tor_emp_dlg.dlg"),"rb").read())
print("DLG entries/replies:", len(dlg.fields["EntryList"][1]), len(dlg.fields["ReplyList"][1]))
print("TLK strrefs:", refs)
print("emperor conversation:", gfftool.read(open(os.path.join(OVR,"tor_emperor.utc"),"rb").read())[2].fields["Conversation"][1])
print("OK -> warp tor_nath, then talk to The Sith Emperor")
