"""Build Revan's player gear for TSL.

- Revan's Robes: a Jedi-robe item with the Disguise item-property, which turns
  the wearer into the Unique_Darth_Revan appearance (appearance.2da row 22).
  i.e. equip it and the player *becomes* Revan.

(The custom lightsaber is built by the Blender model pipeline; its UTI is
installed alongside as tor_revsaber.)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import bif, gfftool
from gfftool import RESREF, LOCSTR, CEXOSTR, Struct

K2 = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
OVR = os.path.join(K2, "Override")
bif.GAME = K2; bifs, res = bif.load_key()

DISGUISE_PROP = 59          # itempropdef "Disguise"; Subtype indexes appearance.2da
REVAN_APPEARANCE = 22       # appearance.2da "Unique_Darth_Revan"

def build_revan_robe():
    _, _, t = gfftool.read(bif.extract("a_robe_02", 2025, bifs, res))   # clone a real robe (correct fields)
    proto = t.fields["PropertiesList"][1][0]
    disg = Struct(proto.stype, dict(proto.fields))
    disg.fields["PropertyName"] = (disg.fields["PropertyName"][0], DISGUISE_PROP)
    disg.fields["Subtype"] = (disg.fields["Subtype"][0], REVAN_APPEARANCE)
    disg.fields["CostTable"] = (disg.fields["CostTable"][0], 255)        # no cost table
    disg.fields["CostValue"] = (disg.fields["CostValue"][0], 0)
    for k, val in [("Param1", 255), ("Param1Value", 0), ("ChanceAppear", 100)]:
        if k in disg.fields:
            disg.fields[k] = (disg.fields[k][0], val)
    t.fields["TemplateResRef"] = (RESREF, "tor_revanrobe")
    t.fields["Tag"] = (CEXOSTR, "tor_revanrobe")
    t.fields["LocalizedName"] = (LOCSTR, (-1, [(0, "Revan's Robes")]))
    t.fields["Description"] = (LOCSTR, (-1, []))
    t.fields["DescIdentified"] = (LOCSTR, (-1, [(0, "The robes of the Prodigal Knight. Worn to take on the guise of Revan.")]))
    t.fields["PropertiesList"] = (15, [disg])
    t.fields["Comment"] = (CEXOSTR, "")
    gfftool.write(os.path.join(OVR, "tor_revanrobe.uti"), "UTI ", "V3.2", t)
    return "tor_revanrobe"

if __name__ == "__main__":
    print("built", build_revan_robe(), "-> giveitem tor_revanrobe (equip to become Revan)")
