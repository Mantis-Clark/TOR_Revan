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
APP_DARTH_REVAN = 22        # appearance.2da "Unique_Darth_Revan" (masked)
APP_JEDI_MALE   = 34        # appearance.2da "Jedi_Council_Member_Male" (robed, unmasked)

def _build_disguise_robe(resref, name, desc, appearance):
    _, _, t = gfftool.read(bif.extract("a_robe_02", 2025, bifs, res))   # clone a real robe (correct fields)
    proto = t.fields["PropertiesList"][1][0]
    disg = Struct(proto.stype, dict(proto.fields))
    disg.fields["PropertyName"] = (disg.fields["PropertyName"][0], DISGUISE_PROP)
    disg.fields["Subtype"] = (disg.fields["Subtype"][0], appearance)
    disg.fields["CostTable"] = (disg.fields["CostTable"][0], 255)        # no cost table
    disg.fields["CostValue"] = (disg.fields["CostValue"][0], 0)
    for k, val in [("Param1", 255), ("Param1Value", 0), ("ChanceAppear", 100)]:
        if k in disg.fields:
            disg.fields[k] = (disg.fields[k][0], val)
    t.fields["TemplateResRef"] = (RESREF, resref)
    t.fields["Tag"] = (CEXOSTR, resref)
    t.fields["LocalizedName"] = (LOCSTR, (-1, [(0, name)]))
    t.fields["Description"] = (LOCSTR, (-1, []))
    t.fields["DescIdentified"] = (LOCSTR, (-1, [(0, desc)]))
    t.fields["PropertiesList"] = (15, [disg])
    t.fields["Comment"] = (CEXOSTR, "")
    gfftool.write(os.path.join(OVR, resref + ".uti"), "UTI ", "V3.2", t)
    return resref

def build_revan_robe():
    return _build_disguise_robe("tor_revanrobe", "Revan's Robes",
        "The mask and robes of the Prodigal Knight, worn to take on the guise of Revan.", APP_DARTH_REVAN)

def build_revan_jedi_robe():
    return _build_disguise_robe("tor_revanjedi", "Revan's Jedi Robes",
        "The robes Revan wears as a Knight of the Order, his face unhidden.", APP_JEDI_MALE)

def build_revan_saber_uti():
    """Revan's lightsaber. Uses the STOCK TSL saber model + icon (clone of a real
    saber, model variation unchanged) so it just works in-game. (A custom hilt model
    is a later art task; the K1->K2 export needs the correct game-mode function pointers.)"""
    _, _, t = gfftool.read(bif.extract("g_w_lghtsbr01", 2025, bifs, res))  # clone a real stock saber
    t.fields["TemplateResRef"] = (RESREF, "tor_revsaber")
    t.fields["Tag"] = (CEXOSTR, "tor_revsaber")
    t.fields["LocalizedName"] = (LOCSTR, (-1, [(0, "Revan's Lightsaber")]))
    # BaseItem and ModelVariation kept from the stock template -> stock model/icon
    gfftool.write(os.path.join(OVR, "tor_revsaber.uti"), "UTI ", "V3.2", t)
    return "tor_revsaber"

if __name__ == "__main__":
    print("built", build_revan_robe(), "-> giveitem tor_revanrobe (become Darth Revan, masked)")
    print("built", build_revan_jedi_robe(), "-> giveitem tor_revanjedi (become Jedi Revan, unmasked)")
    print("built", build_revan_saber_uti(), "-> giveitem tor_revsaber (needs model from blender/kitbash_saber_tsl.py)")
