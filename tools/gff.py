import struct, sys

# Minimal GFF reader for inspection
def read_gff(path):
    d = open(path,'rb').read()
    ftype = d[:4]; ver = d[4:8]
    (struct_off,struct_cnt,field_off,field_cnt,label_off,label_cnt,
     fdata_off,fdata_cnt,fidx_off,fidx_cnt,lidx_off,lidx_cnt) = struct.unpack_from('<12I',d,8)
    labels=[]
    for i in range(label_cnt):
        labels.append(d[label_off+i*16:label_off+i*16+16].split(b'\x00')[0].decode('ascii'))
    fields=[]
    for i in range(field_cnt):
        ftypeid,flabel,fdataoff = struct.unpack_from('<III',d,field_off+i*12)
        fields.append((ftypeid,flabel,fdataoff))
    structs=[]
    for i in range(struct_cnt):
        sid,dataoff,cnt = struct.unpack_from('<iII',d,struct_off+i*12)
        structs.append((sid,dataoff,cnt))
    return d,labels,fields,structs,fdata_off,fidx_off

TYPES={0:'BYTE',1:'CHAR',2:'WORD',3:'SHORT',4:'DWORD',5:'INT',6:'DWORD64',7:'INT64',
8:'FLOAT',9:'DOUBLE',10:'CExoString',11:'ResRef',12:'CExoLocString',13:'VOID',
14:'Struct',15:'List'}

def dump(path):
    d,labels,fields,structs,fdata_off,fidx_off=read_gff(path)
    print("LABELS:",len(labels),"FIELDS:",len(fields),"STRUCTS:",len(structs))
    for i,(ftypeid,flabel,fdataoff) in enumerate(fields):
        t=TYPES.get(ftypeid,str(ftypeid))
        lab=labels[flabel]
        val=''
        if ftypeid in (0,1,2,3,4,5):
            val=fdataoff  # stored inline (need signedness but ok)
            if ftypeid==2: val=fdataoff & 0xFFFF
        elif ftypeid==8:
            val=struct.unpack('<f',struct.pack('<I',fdataoff))[0]
        elif ftypeid==10:
            sz=struct.unpack_from('<I',d,fdata_off+fdataoff)[0]
            val=d[fdata_off+fdataoff+4:fdata_off+fdataoff+4+sz].decode('ascii','replace')
        elif ftypeid==11:
            sz=d[fdata_off+fdataoff]
            val=d[fdata_off+fdataoff+1:fdata_off+fdataoff+1+sz].decode('ascii','replace')
        elif ftypeid==12:
            total=struct.unpack_from('<I',d,fdata_off+fdataoff)[0]
            val='<locstring>'
        print(f'[{i}] {lab} : {t} = {val}')

if __name__=='__main__':
    dump(sys.argv[1])
