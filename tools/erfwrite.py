"""Writer for KOTOR/TSL ERF/MOD/HAK archives. Pairs with erf.py (reader)."""
import struct

def write(path, entries, filetype="MOD "):
    """entries: list of (resref:str, restype:int, data:bytes), order preserved."""
    n = len(entries)
    HDR = 160
    loc_off = HDR          # localized string list (empty)
    key_off = loc_off + 0
    res_off = key_off + n * 24
    data_off = res_off + n * 8

    keyblock = bytearray(); resblock = bytearray(); datablock = bytearray()
    cur = data_off
    for i, (rr, rt, data) in enumerate(entries):
        rb = rr.lower().encode("ascii")[:16]
        rb = rb + b"\x00" * (16 - len(rb))
        keyblock += rb + struct.pack("<IHH", i, rt, 0)
        resblock += struct.pack("<II", cur, len(data))
        datablock += data
        cur += len(data)

    out = bytearray()
    out += filetype.encode("ascii")[:4].ljust(4) + b"V1.0"
    out += struct.pack("<9I",
        0,            # LanguageCount
        0,            # LocalizedStringSize
        n,            # EntryCount
        loc_off,      # OffsetToLocalizedString
        key_off,      # OffsetToKeyList
        res_off,      # OffsetToResourceList
        126,          # BuildYear (2026-1900)
        1,            # BuildDay
        0xFFFFFFFF)   # DescriptionStrRef
    out += b"\x00" * 116
    assert len(out) == HDR, len(out)
    out += keyblock + resblock + datablock
    if path:
        open(path, "wb").write(out)
    return bytes(out)
