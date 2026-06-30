import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import rim, gfftool, bif, os
from gfftool import Struct, RESREF, LOCSTR, CEXOSTR, FLOAT

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override"); MODS = os.path.join(K2, "modules")
bif.GAME = K2; bifs, res = bif.load_key()

# 1) custom NPC: The Sith Emperor (based on Nihilus, neutral so he just stands)
_, _, utc = gfftool.read(bif.extract("n_darthnihilus", 2027, bifs, res))
utc.fields["FirstName"] = (LOCSTR, (-1, [(0, "The Sith Emperor")]))
utc.fields["Tag"] = (CEXOSTR, "tor_emperor")
utc.fields["TemplateResRef"] = (RESREF, "tor_emperor")
fac_t = utc.fields["FactionID"][0]
utc.fields["FactionID"] = (fac_t, 5)   # Neutral
gfftool.write(os.path.join(OVR, "tor_emperor.utc"), "UTI " if False else "UTC ", "V3.2", utc)

# 2) load Korriban academy module resources
ents = rim.read_rim(os.path.join(MODS, "702KOR.rim"))
are_bytes = next(d for r, t, d in ents if t == 2012)
git_bytes = next(d for r, t, d in ents if t == 2023)
ifo_bytes = next(d for r, t, d in ents if t == 2014)

# 3) customize GIT: replace creatures with just our Emperor at the entry hall
_, _, gt = gfftool.read(git_bytes)
proto = gt.fields["Creature List"][1][0]
emp = Struct(proto.stype, dict(proto.fields))
emp.fields["TemplateResRef"] = (RESREF, "tor_emperor")
emp.fields["XPosition"] = (FLOAT, 121.6)
emp.fields["YPosition"] = (FLOAT, 150.0)
emp.fields["ZPosition"] = (FLOAT, 0.15)
emp.fields["XOrientation"] = (FLOAT, 0.0)
emp.fields["YOrientation"] = (FLOAT, 1.0)
gt.fields["Creature List"] = (gt.fields["Creature List"][0], [emp])
git_out = gfftool.write(None, "GIT ", "V3.2", gt)

# 4) IFO: retag the module (keeps area 702kor + entry point so geometry loads from BIF)
_, _, it = gfftool.read(ifo_bytes)
it.fields["Mod_Tag"] = (CEXOSTR, "tor_nath")
ifo_out = gfftool.write(None, "IFO ", "V3.2", it)

# 5) assemble walkable module
rim.write_rim(os.path.join(MODS, "tor_nath.rim"),
              [("702kor", 2012, are_bytes), ("702kor", 2023, git_out), ("module", 2014, ifo_out)])

# 6) validate the assembled module round-trips and contains our spawn
chk = rim.read_rim(os.path.join(MODS, "tor_nath.rim"))
_, _, gt2 = gfftool.read(next(d for r, t, d in chk if t == 2023))
cl = gt2.fields["Creature List"][1]
print("module written. creatures:", [c.fields["TemplateResRef"][1] for c in cl])
print("entry area:", gfftool.read(next(d for r, t, d in chk if t == 2014))[2].fields["Mod_Entry_Area"][1])
print("emperor utc name:", gfftool.read(open(os.path.join(OVR,'tor_emperor.utc'),'rb').read())[2].fields["FirstName"][1])
print("OK -> warp tor_nath")
