#!/usr/bin/env python3
"""TOR_Revan build orchestrator.

One command: generate GFF resources, compile scripts, pack modules, and install.
Run:  python build.py            # build into ./build
      python build.py --install  # also copy into the TSL game folders
"""
import os, sys, glob, argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gfftool, erfwrite, nsscomp, tlk
from gfftool import Struct, RESREF, INT, LOCSTR, CEXOSTR, BYTE, DWORD, WORD, LIST

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Knights of the Old Republic II"
BUILD = os.path.join(ROOT, "build")
OUT_OVR = os.path.join(BUILD, "Override")
OUT_MOD = os.path.join(BUILD, "modules")

# Restypes
RT_UTI, RT_IFO, RT_NCS = 2025, 2014, 2010


def make_belt_uti(resref, name, desc, baseitem=47, modelvar=1):
    s = Struct(-1); f = s.fields
    f["TemplateResRef"] = (RESREF, resref)
    f["BaseItem"] = (INT, baseitem)
    f["LocalizedName"] = (LOCSTR, (-1, [(0, name)]))
    f["Description"] = (LOCSTR, (-1, []))
    f["DescIdentified"] = (LOCSTR, (-1, [(0, desc)]))
    f["Tag"] = (CEXOSTR, resref)
    f["Charges"] = (BYTE, 0); f["Cost"] = (DWORD, 100); f["Stolen"] = (BYTE, 0)
    f["StackSize"] = (WORD, 1); f["Plot"] = (BYTE, 0); f["AddCost"] = (DWORD, 0)
    f["Identified"] = (BYTE, 1); f["UpgradeLevel"] = (BYTE, 0)
    f["ModelVariation"] = (BYTE, modelvar); f["PropertiesList"] = (LIST, [])
    f["PaletteID"] = (BYTE, 16); f["Comment"] = (CEXOSTR, "TOR_Revan")
    return gfftool.write(None, "UTI ", "V3.2", s)


# --- mod content registry (grows as the mod grows) ---
ITEMS = [
    dict(resref="tor_testbelt", name="TOR Test Belt",
         desc="Generated from scratch by the TOR_Revan build."),
]


def build_items():
    os.makedirs(OUT_OVR, exist_ok=True)
    for it in ITEMS:
        data = make_belt_uti(it["resref"], it["name"], it["desc"])
        open(os.path.join(OUT_OVR, it["resref"] + ".uti"), "wb").write(data)
    return len(ITEMS)


def build_scripts(game="K2"):
    os.makedirs(OUT_OVR, exist_ok=True)
    n = 0
    for nss in glob.glob(os.path.join(ROOT, "scripts", "*.nss")):
        out = os.path.join(OUT_OVR, os.path.splitext(os.path.basename(nss))[0] + ".ncs")
        nsscomp.compile_file(nss, out, game)
        n += 1
    return n


def build_demo_module():
    os.makedirs(OUT_MOD, exist_ok=True)
    ifo = Struct(-1)
    ifo.fields["Mod_Tag"] = (CEXOSTR, "tor_test_mod")
    ifo.fields["Mod_Entry_Area"] = (RESREF, "tor_test")
    ifo_bytes = gfftool.write(None, "IFO ", "V3.2", ifo)
    uti = make_belt_uti("tor_testbelt", "TOR Test Belt", "demo")
    entries = [("module", RT_IFO, ifo_bytes), ("tor_testbelt", RT_UTI, uti)]
    erfwrite.write(os.path.join(OUT_MOD, "tor_demo.mod"), entries, "MOD ")
    return "tor_demo.mod"


def install():
    import shutil
    for f in glob.glob(os.path.join(OUT_OVR, "*")):
        shutil.copy2(f, os.path.join(GAME, "Override", os.path.basename(f)))
    for f in glob.glob(os.path.join(OUT_MOD, "*")):
        shutil.copy2(f, os.path.join(GAME, "modules", os.path.basename(f)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--game", default="K2")
    a = ap.parse_args()
    ni = build_items()
    ns = build_scripts(a.game)
    mod = build_demo_module()
    print(f"built: {ni} item(s), {ns} script(s), module {mod}  ->  {BUILD}")
    if a.install:
        install()
        print(f"installed to {GAME}")


if __name__ == "__main__":
    main()
