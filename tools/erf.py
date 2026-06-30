import struct, os, glob

GAME = r'C:/Program Files (x86)/Steam/steamapps/common/swkotor'

RESTYPES = {2009:'nss',2010:'ncs',2025:'uti',2027:'utc',2029:'dlg',2023:'utp',
            2017:'2da',2035:'ncs2',2042:'jrl',2014:'are',2015:'ifo',2016:'git',
            2022:'utt',2024:'utw',2026:'ute',2028:'uts',2031:'utm',2032:'utd'}

def read_erf(path):
    d = open(path,'rb').read()
    sig = d[:8]
    assert sig[:3] in (b'MOD', b'ERF', b'SAV', b'HAK', b'RIM'), sig
    if sig[:3]==b'RIM':
        return read_rim(d)
    (lang, lss, entrycnt, locoff, keyoff, resoff) = struct.unpack_from('<6I', d, 8)
    entries=[]
    for i in range(entrycnt):
        base=keyoff+i*24
        resref=d[base:base+16].split(b'\x00')[0].decode('ascii','replace').lower()
        resid,restype = struct.unpack_from('<IH', d, base+16)
        roff,rsize = struct.unpack_from('<II', d, resoff+i*8)
        entries.append((resref,restype,roff,rsize))
    return d, entries

def read_rim(d):
    cnt, tableoff = struct.unpack_from('<II', d, 8+4)  # reserved then... fallback
    return d, []

def iter_resources(path):
    d, entries = read_erf(path)
    for resref,restype,roff,rsize in entries:
        yield resref, restype, d[roff:roff+rsize]

if __name__=='__main__':
    import sys
    want = int(sys.argv[1]) if len(sys.argv)>1 else 2025
    mods = sorted(glob.glob(os.path.join(GAME,'modules','bos_*.mod')))
    for m in mods:
        try:
            d,entries=read_erf(m)
        except Exception as e:
            print("ERR",os.path.basename(m),e); continue
        hits=[r for (r,t,o,s) in entries if t==want]
        if hits:
            print(os.path.basename(m), '->', len(hits), 'resources type', want)
