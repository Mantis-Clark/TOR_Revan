"""Reader/writer for KOTOR/TSL RIM archives (RIM V1.0).

Header (120 bytes): 'RIM ' 'V1.0' reserved(u32) ResourceCount(u32)
                    OffsetToResourceTable(u32) ... reserved
Entry (32 bytes): ResRef(16) ResType(u32) ResIndex(u32) Offset(u32) Size(u32)
"""
import struct

def read_rim(path):
    d = path if isinstance(path,(bytes,bytearray)) else open(path,"rb").read()
    assert d[:8] == b"RIM V1.0", d[:8]
    count = struct.unpack_from("<I", d, 12)[0]
    table = struct.unpack_from("<I", d, 16)[0]
    out = []
    for i in range(count):
        base = table + i*32
        rr = d[base:base+16].split(b"\x00")[0].decode("latin-1").lower()
        rtype, ridx, off, size = struct.unpack_from("<IIII", d, base+16)
        out.append((rr, rtype, d[off:off+size]))
    return out

def write_rim(path, entries):
    """entries: list of (resref, restype, data)."""
    n = len(entries)
    table = 120
    data_off = table + n*32
    head = bytearray(120)
    head[0:8] = b"RIM V1.0"
    struct.pack_into("<I", head, 12, n)
    struct.pack_into("<I", head, 16, table)
    tbl = bytearray(); blob = bytearray(); cur = data_off
    for i,(rr,rt,data) in enumerate(entries):
        rb = rr.lower().encode("latin-1")[:16]; rb += b"\x00"*(16-len(rb))
        tbl += rb + struct.pack("<IIII", rt, i, cur, len(data))
        blob += data; cur += len(data)
    out = bytes(head) + bytes(tbl) + bytes(blob)
    if path: open(path,"wb").write(out)
    return out
