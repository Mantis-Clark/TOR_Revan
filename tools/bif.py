import struct, os

GAME=r'C:/Program Files (x86)/Steam/steamapps/common/swkotor'

def load_key():
    d=open(os.path.join(GAME,'chitin.key'),'rb').read()
    assert d[:8]==b'KEY V1  ',d[:8]
    bifcnt,rescnt,fileoff,keyoff=struct.unpack_from('<IIII',d,8)
    bifs=[]
    for i in range(bifcnt):
        fsize,fnoff,fnsize,drives=struct.unpack_from('<IIHH',d,fileoff+i*12)
        name=d[fnoff:fnoff+fnsize].split(b'\x00')[0].decode('ascii')
        bifs.append(name.replace('\\','/'))
    res={}
    for i in range(rescnt):
        base=keyoff+i*22
        resref=d[base:base+16].split(b'\x00')[0].decode('ascii').lower()
        restype,resid=struct.unpack_from('<HI',d,base+16)
        bifidx=resid>>20
        varidx=resid & 0xFFFFF
        res[(resref,restype)]=(bifidx,varidx)
    return bifs,res

def extract(resref,restype,bifs,res):
    key=(resref.lower(),restype)
    if key not in res: return None
    bifidx,varidx=res[key]
    bifpath=os.path.join(GAME,bifs[bifidx])
    d=open(bifpath,'rb').read()
    assert d[:8]==b'BIFFV1  ',d[:8]
    varcnt,fixcnt,varoff=struct.unpack_from('<III',d,8)
    base=varoff+varidx*16
    rid,off,sz,rt=struct.unpack_from('<IIII',d,base)
    return d[off:off+sz]

if __name__=='__main__':
    import sys
    bifs,res=load_key()
    # restypes: 2da=2017, uti=2025
    out=extract(sys.argv[1],int(sys.argv[2]),bifs,res)
    if out is None:
        print("NOT FOUND")
    else:
        open(sys.argv[3],'wb').write(out)
        print("WROTE",len(out),"bytes to",sys.argv[3])
