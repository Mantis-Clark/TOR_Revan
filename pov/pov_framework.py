"""3-POV switching framework (Revan / Lord Scourge / Meetra Surik) for TSL.

KOTOR's real mechanism for controlling multiple characters is the party system:
party members are registered to npc.2da slots (AddAvailableNPCByTemplate), spawned
(SpawnAvailableNPC) and added (AddPartyMember); the player switches who they control
via the native party UI / SetPartyLeader. This is exactly what TSL's prologue uses.

This builds the two non-PC protagonists as party-member templates and an init script
that puts all three protagonists in the party. It hooks the init to tor_nath's area
OnEnter, so `warp tor_nath` drops you in with Revan (PC) + Scourge + Meetra, switchable.

Reusable pattern: call TOR party setup from any act's OnEnter with the act's roster.
Appearances are robed stand-ins (no canonical KOTOR models for a Sith Pureblood or
the Exile): Scourge -> Dark_Jedi_Master_01 (379), Meetra -> Jedi_Council_Member_Female (33).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import bif, erf, erfwrite, gfftool
from gfftool import RESREF, LOCSTR, CEXOSTR
from pykotor.resource.formats.ncs import compile_nss, bytes_ncs
from pykotor.common.misc import Game

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override"); MODS = os.path.join(K2, "modules")
bif.GAME = K2; bifs, res = bif.load_key()

def make_member(resref, name, appearance, gender):
    _, _, t = gfftool.read(bif.extract("p_atton", 2027, bifs, res))   # clone a real member (valid class/stats/flags)
    t.fields["FirstName"] = (LOCSTR, (-1, [(0, name)]))
    t.fields["Tag"] = (CEXOSTR, resref)
    t.fields["TemplateResRef"] = (RESREF, resref)
    t.fields["Appearance_Type"] = (t.fields["Appearance_Type"][0], appearance)
    t.fields["Conversation"] = (t.fields["Conversation"][0], "")
    if "Gender" in t.fields: t.fields["Gender"] = (t.fields["Gender"][0], gender)
    gfftool.write(os.path.join(OVR, resref + ".utc"), "UTC ", "V3.2", t)
    return resref

make_member("tor_p_scourge", "Lord Scourge", 379, 0)
make_member("tor_p_meetra", "Meetra Surik", 33, 1)

# init script: add Scourge (slot 0) and Meetra (slot 1) to the party, once.
INIT = '''
void main() {
    object oPC = GetFirstPC();
    if (GetLocalBoolean(oPC, 60)) return;
    SetLocalBoolean(oPC, 60, TRUE);
    location l = GetLocation(oPC);
    AddAvailableNPCByTemplate(0, "tor_p_scourge");
    object oS = SpawnAvailableNPC(0, l);
    AddPartyMember(0, oS);
    AddAvailableNPCByTemplate(1, "tor_p_meetra");
    object oM = SpawnAvailableNPC(1, l);
    AddPartyMember(1, oM);
}
'''
open(os.path.join(OVR, "tor_pov_init.ncs"), "wb").write(bytes(bytes_ncs(compile_nss(INIT, Game.K2))))

# hook the init to tor_nath's area OnEnter (rewrite the .mod's ARE)
d, ents = erf.read_erf(os.path.join(MODS, "tor_nath.mod"))
out_files = []
for r, t, o, s in ents:
    blob = d[o:o+s]
    if t == 2012:  # ARE
        _, _, are = gfftool.read(blob)
        are.fields["OnEnter"] = (are.fields["OnEnter"][0], "tor_pov_init")
        blob = gfftool.write(None, "ARE ", "V3.2", are)
    out_files.append((r, t, blob))
erfwrite.write(os.path.join(MODS, "tor_nath.mod"), out_files, "MOD ")

print("POV framework built: tor_p_scourge.utc, tor_p_meetra.utc, tor_pov_init.ncs")
print("hooked tor_nath OnEnter -> tor_pov_init. warp tor_nath: you (Revan) + Scourge + Meetra, switch via party UI.")
