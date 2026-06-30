"""Reader + appender for KOTOR/TSL dialog.tlk (TLK V3.0).

Header(20): 'TLK ' 'V3.0' LanguageID(u32) StringCount(u32) StringEntriesOffset(u32)
Then StringCount x 40-byte data elements:
  Flags(u32) SoundResRef(16) VolumeVariance(u32) PitchVariance(u32)
  OffsetToString(u32, rel to StringEntriesOffset) StringSize(u32) SoundLength(f32)
Then string data block.
"""
import struct

TEXT_PRESENT = 0x01

def read(path):
    d = open(path, "rb").read()
    assert d[:8] == b"TLK V3.0", d[:8]
    lang, count, entries_off = struct.unpack_from("<III", d, 8)
    strings = []
    for i in range(count):
        base = 20 + i * 40
        flags, = struct.unpack_from("<I", d, base)
        snd = d[base+4:base+20].split(b"\x00")[0].decode("latin-1")
        vol, pitch, soff, ssize = struct.unpack_from("<IIII", d, base+20)
        slen, = struct.unpack_from("<f", d, base+36)
        text = d[entries_off+soff:entries_off+soff+ssize].decode("latin-1") if flags & TEXT_PRESENT else ""
        strings.append({"flags": flags, "snd": snd, "vol": vol, "pitch": pitch,
                        "text": text, "soundlen": slen})
    return lang, strings

def write(path, lang, strings):
    count = len(strings)
    entries_off = 20 + count * 40
    data = bytearray(); elems = bytearray()
    for s in strings:
        text = s.get("text", "")
        tb = text.encode("latin-1")
        soff = len(data); ssize = len(tb)
        data += tb
        snd = s.get("snd", "").encode("latin-1")[:16]; snd = snd + b"\x00"*(16-len(snd))
        flags = s.get("flags", TEXT_PRESENT if text else 0)
        elems += struct.pack("<I", flags) + snd + struct.pack("<IIIIf",
            s.get("vol",0), s.get("pitch",0), soff, ssize, s.get("soundlen",0.0))
    out = bytearray()
    out += b"TLK V3.0" + struct.pack("<III", lang, count, entries_off)
    out += elems + data
    if path: open(path, "wb").write(out)
    return bytes(out)

def append(path, new_texts, lang=None):
    """Append list[str] to the TLK; returns (new_strref_list). Saves in place."""
    cur_lang, strings = read(path)
    if lang is None: lang = cur_lang
    first = len(strings)
    refs = []
    for t in new_texts:
        refs.append(len(strings))
        strings.append({"flags": TEXT_PRESENT, "snd": "", "vol": 0, "pitch": 0,
                        "text": t, "soundlen": 0.0})
    write(path, lang, strings)
    return refs
