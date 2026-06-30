import struct, sys

def read_2da(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:8] == b'2DA V2.b', data[:8]
    pos = 8
    assert data[pos] == 0x0A
    pos += 1
    # columns: tab-terminated strings until a 0x00
    cols = []
    while data[pos] != 0x00:
        end = data.index(0x09, pos)
        cols.append(data[pos:end].decode('ascii'))
        pos = end + 1
    pos += 1  # skip the 0x00
    rowcount = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    # row labels: rowcount tab-terminated strings
    rowlabels = []
    for _ in range(rowcount):
        end = data.index(0x09, pos)
        rowlabels.append(data[pos:end].decode('ascii'))
        pos = end + 1
    ncells = rowcount * len(cols)
    offsets = struct.unpack_from('<%dH' % ncells, data, pos)
    pos += 2 * ncells
    pos += 2  # 2-byte field after offsets is unreliable (often 0); data runs to EOF
    datablock = data[pos:]
    # decode cells
    def getstr(off):
        end = datablock.index(0x00, off)
        return datablock[off:end].decode('ascii')
    cells = []
    for r in range(rowcount):
        row = []
        for c in range(len(cols)):
            row.append(getstr(offsets[r*len(cols)+c]))
        cells.append(row)
    return cols, rowlabels, cells

def write_2da(path, cols, rowlabels, cells):
    out = bytearray(b'2DA V2.b\n')
    for c in cols:
        out += c.encode('ascii') + b'\x09'
    out += b'\x00'
    out += struct.pack('<I', len(rowlabels))
    for rl in rowlabels:
        out += rl.encode('ascii') + b'\x09'
    # build dedup data block
    datablock = bytearray()
    strmap = {}
    def addstr(s):
        if s in strmap:
            return strmap[s]
        off = len(datablock)
        strmap[s] = off
        datablock.extend(s.encode('ascii') + b'\x00')
        return off
    offsets = []
    for r in range(len(rowlabels)):
        for c in range(len(cols)):
            offsets.append(addstr(cells[r][c]))
    for o in offsets:
        out += struct.pack('<H', o)
    out += struct.pack('<H', len(datablock))
    out += datablock
    with open(path, 'wb') as f:
        f.write(out)

if __name__ == '__main__':
    cols, rl, cells = read_2da(sys.argv[1])
    print("ROWS:", len(rl), "COLS:", len(cols))
    print("COLUMNS:", cols)
    # show impactscript column index
    if 'impactscript' in cols:
        ic = cols.index('impactscript')
        # find rows with non-empty impactscript
        found = [(rl[r], cells[r][ic]) for r in range(len(rl)) if cells[r][ic] not in ('', '****')]
        print("ROWS WITH impactscript (first 15):", found[:15])
    print("LAST ROW label:", rl[-1])
    print("LAST ROW cells:", cells[-1])
