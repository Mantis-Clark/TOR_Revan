"""Append a quest to global.jrl (the global journal). Reusable.

A quest = a Category (Tag is the plot ID used by AddJournalQuestEntry) holding
Entry structs (ID = state number, End = quest-complete flag, Text = TLK strref).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bif, gfftool, tlk
from gfftool import Struct, CEXOSTR, LOCSTR


def append_quest(game_dir, tag, name, entries):
    """entries: list of (state_id:int, text:str, is_end:bool). Idempotent on tag."""
    bif.GAME = game_dir
    bifs, res = bif.load_key()
    ovr = os.path.join(game_dir, "Override")
    jpath = os.path.join(ovr, "global.jrl")
    raw = open(jpath, "rb").read() if os.path.exists(jpath) else bif.extract("global", 2056, bifs, res)
    ft, ver, t = gfftool.read(raw)
    cats = t.fields["Categories"][1]
    cat_proto = cats[0]
    entry_proto = cat_proto.fields["EntryList"][1][0]

    # idempotent: drop any existing category with our tag
    cats = [c for c in cats if c.fields.get("Tag", (0, ""))[1] != tag]

    # TLK strings for name + entry texts
    refs = tlk.append(os.path.join(game_dir, "dialog.tlk"), [name] + [e[1] for e in entries])
    name_ref, entry_refs = refs[0], refs[1:]

    cat = Struct(cat_proto.stype, dict(cat_proto.fields))
    cat.fields["Name"] = (LOCSTR, (name_ref, []))
    cat.fields["Tag"] = (CEXOSTR, tag)
    cat.fields["Comment"] = (CEXOSTR, "")
    ent_structs = []
    for (sid, text, is_end), tref in zip(entries, entry_refs):
        e = Struct(entry_proto.stype, dict(entry_proto.fields))
        e.fields["ID"] = (e.fields["ID"][0], sid)
        e.fields["End"] = (e.fields["End"][0], 1 if is_end else 0)
        e.fields["Text"] = (LOCSTR, (tref, []))
        ent_structs.append(e)
    cat.fields["EntryList"] = (15, ent_structs)

    cats.append(cat)
    t.fields["Categories"] = (15, cats)
    gfftool.write(jpath, ft, ver, t)
    return tag
