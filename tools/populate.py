"""Reusable helpers to populate Act I modules with neutral ambient NPCs.

ambient_utc(): clones a valid base creature UTC (p_atton 2027 from BIF, so its
class/stats/feats/flags are all valid), then overrides only the identity fields
(name, tag, resref, appearance, faction, no dialogue) and writes it to Override.

append_creature(): appends a GIT creature spawn struct (cloned from a real GIT
creature proto, so all spawn fields stay valid) to a GIT's 'Creature List'.

Ambient NPCs are FactionID=5 (Neutral) so they never attack the player and have
no Conversation, so they are pure scenery / atmosphere.
"""
import os
import bif, gfftool
from gfftool import Struct, RESREF, LOCSTR, CEXOSTR, FLOAT


def ambient_utc(resref, name, appearance, bifs, res, ovr, faction=5, base="p_atton"):
    """Build a neutral, mute ambient creature UTC and write it to Override.

    resref      : unique template resref / tag for the creature
    name        : display FirstName (inline LocString, original text only)
    appearance  : Appearance_Type row index from appearance.2da
    bifs, res   : loaded chitin key tables (bif.load_key())
    ovr         : Override directory to write <resref>.utc into
    faction     : FactionID (default 5 = Neutral, never hostile)
    base        : valid base creature to clone for stats/flags (default p_atton)
    Returns the resref.
    """
    _, _, utc = gfftool.read(bif.extract(base, 2027, bifs, res))
    utc.fields["FirstName"] = (LOCSTR, (-1, [(0, name)]))
    utc.fields["Tag"] = (CEXOSTR, resref)
    utc.fields["TemplateResRef"] = (RESREF, resref)
    utc.fields["Appearance_Type"] = (utc.fields["Appearance_Type"][0], appearance)
    utc.fields["FactionID"] = (utc.fields["FactionID"][0], faction)
    utc.fields["Conversation"] = (utc.fields.get("Conversation", (RESREF, ""))[0], "")
    gfftool.write(os.path.join(ovr, resref + ".utc"), "UTC ", "V3.2", utc)
    return resref


def append_creature(gt, proto, resref, x, y, z, ox=0.0, oy=1.0):
    """Clone a GIT creature proto and append a spawn for `resref` to Creature List.

    gt    : the GIT Struct
    proto : a valid GIT creature Struct to clone all spawn fields from
    x,y,z : world position
    ox,oy : 2D facing orientation (unit vector)
    Returns the new spawn Struct.
    """
    c = Struct(proto.stype, dict(proto.fields))
    c.fields["TemplateResRef"] = (RESREF, resref)
    c.fields["XPosition"] = (FLOAT, x)
    c.fields["YPosition"] = (FLOAT, y)
    c.fields["ZPosition"] = (FLOAT, z)
    c.fields["XOrientation"] = (FLOAT, ox)
    c.fields["YOrientation"] = (FLOAT, oy)
    gt.fields["Creature List"][1].append(c)
    return c
