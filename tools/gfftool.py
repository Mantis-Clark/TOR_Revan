"""Full GFF reader/writer for KOTOR/TSL (tree model).

Types: 0 BYTE,1 CHAR,2 WORD,3 SHORT,4 DWORD,5 INT,6 DWORD64,7 INT64,8 FLOAT,
9 DOUBLE,10 CExoString,11 ResRef,12 CExoLocString,13 VOID,14 Struct,15 List.
"""
import struct

BYTE,CHAR,WORD,SHORT,DWORD,INT,DWORD64,INT64,FLOAT,DOUBLE,CEXOSTR,RESREF,LOCSTR,VOID,STRUCT,LIST = range(16)
SIMPLE_INLINE = {BYTE,CHAR,WORD,SHORT,DWORD,INT,FLOAT}

class Struct:
    __slots__=("stype","fields")
    def __init__(self, stype=-1, fields=None):
        self.stype = stype
        self.fields = fields if fields is not None else {}   # label -> (ftype, value)
    def __repr__(self): return "Struct(%d, %r)"%(self.stype, self.fields)

# ---------------- reader ----------------
def read(path_or_bytes):
    d = path_or_bytes if isinstance(path_or_bytes,(bytes,bytearray)) else open(path_or_bytes,'rb').read()
    ftype = d[:4].decode('ascii'); ver = d[4:8].decode('ascii')
    (s_off,s_cnt,f_off,f_cnt,l_off,l_cnt,fd_off,fd_cnt,fi_off,fi_cnt,li_off,li_cnt)=struct.unpack_from('<12I',d,8)
    structs=[struct.unpack_from('<iII',d,s_off+i*12) for i in range(s_cnt)]
    fields =[struct.unpack_from('<III',d,f_off+i*12) for i in range(f_cnt)]
    labels =[d[l_off+i*16:l_off+i*16+16].split(b'\x00')[0].decode('ascii') for i in range(l_cnt)]
    def decode(ftypeid, raw):
        if ftypeid==BYTE:  return raw & 0xFF
        if ftypeid==CHAR:  v=raw&0xFF; return v-256 if v>=128 else v
        if ftypeid==WORD:  return raw & 0xFFFF
        if ftypeid==SHORT: v=raw&0xFFFF; return v-65536 if v>=32768 else v
        if ftypeid==DWORD: return raw & 0xFFFFFFFF
        if ftypeid==INT:   return struct.unpack('<i',struct.pack('<I',raw&0xFFFFFFFF))[0]
        if ftypeid==FLOAT: return struct.unpack('<f',struct.pack('<I',raw&0xFFFFFFFF))[0]
        base=fd_off+raw
        if ftypeid==DWORD64: return struct.unpack_from('<Q',d,base)[0]
        if ftypeid==INT64:   return struct.unpack_from('<q',d,base)[0]
        if ftypeid==DOUBLE:  return struct.unpack_from('<d',d,base)[0]
        if ftypeid==CEXOSTR:
            n=struct.unpack_from('<I',d,base)[0]; return d[base+4:base+4+n].decode('latin-1')
        if ftypeid==RESREF:
            n=d[base]; return d[base+1:base+1+n].decode('latin-1')
        if ftypeid==LOCSTR:
            total,strref,cnt=struct.unpack_from('<iiI',d,base) if False else (struct.unpack_from('<I',d,base)[0],struct.unpack_from('<i',d,base+4)[0],struct.unpack_from('<I',d,base+8)[0])
            subs=[]; p=base+12
            for _ in range(cnt):
                sid,ln=struct.unpack_from('<iI',d,p); p+=8
                subs.append((sid, d[p:p+ln].decode('latin-1'))); p+=ln
            return (strref, subs)
        if ftypeid==VOID:
            n=struct.unpack_from('<I',d,base)[0]; return d[base+4:base+4+n]
        raise ValueError("bad complex type %d"%ftypeid)
    def build(si):
        stype,dataoff,fcount=structs[si]
        if fcount==1: idxs=[dataoff]
        elif fcount>1: idxs=list(struct.unpack_from('<%dI'%fcount,d,fi_off+dataoff))
        else: idxs=[]
        st=Struct(stype)
        for fi in idxs:
            ftypeid,flabel,fdata=fields[fi]
            lab=labels[flabel]
            if ftypeid==STRUCT: st.fields[lab]=(STRUCT, build(fdata))
            elif ftypeid==LIST:
                cnt=struct.unpack_from('<I',d,li_off+fdata)[0]
                cidx=struct.unpack_from('<%dI'%cnt,d,li_off+fdata+4) if cnt else []
                st.fields[lab]=(LIST,[build(ci) for ci in cidx])
            else:
                st.fields[lab]=(ftypeid, decode(ftypeid,fdata))
        return st
    return ftype, ver, build(0)

# ---------------- writer ----------------
def write(path, ftype, ver, top):
    assert len(ftype)==4 and len(ver)==4
    flat=[]; idmap={}
    def flatten(s):
        idmap[id(s)]=len(flat); flat.append(s)
        for lab,(ft,val) in s.fields.items():
            if ft==STRUCT: flatten(val)
            elif ft==LIST:
                for c in val: flatten(c)
    flatten(top)

    labels=[]; lab_idx={}
    def label_index(lab):
        if lab not in lab_idx:
            lab_idx[lab]=len(labels); labels.append(lab)
        return lab_idx[lab]

    field_data=bytearray(); field_arr=[]; per_struct_fieldidx=[]
    def enc_complex(ft,val):
        off=len(field_data)
        if ft in (DWORD64,): field_data.extend(struct.pack('<Q',val))
        elif ft==INT64:      field_data.extend(struct.pack('<q',val))
        elif ft==DOUBLE:     field_data.extend(struct.pack('<d',val))
        elif ft==CEXOSTR:
            b=val.encode('latin-1'); field_data.extend(struct.pack('<I',len(b))+b)
        elif ft==RESREF:
            b=val.encode('latin-1'); field_data.extend(bytes([len(b)])+b)
        elif ft==LOCSTR:
            strref,subs=val; body=bytearray(struct.pack('<iI',strref,len(subs)))
            for sid,txt in subs:
                tb=txt.encode('latin-1'); body.extend(struct.pack('<iI',sid,len(tb))+tb)
            field_data.extend(struct.pack('<I',len(body))+body)
        elif ft==VOID:
            field_data.extend(struct.pack('<I',len(val))+bytes(val))
        else: raise ValueError(ft)
        return off
    def inline(ft,val):
        if ft==FLOAT: return struct.unpack('<I',struct.pack('<f',val))[0]
        return val & 0xFFFFFFFF
    for s in flat:
        fidxs=[]
        for lab,(ft,val) in s.fields.items():
            li=label_index(lab)
            if ft in SIMPLE_INLINE: dod=inline(ft,val)
            elif ft==STRUCT: dod=idmap[id(val)]
            elif ft==LIST: dod=val            # placeholder; fix in list pass
            else: dod=enc_complex(ft,val)
            fidxs.append(len(field_arr))
            field_arr.append([ft,li,dod])
        per_struct_fieldidx.append(fidxs)

    # list indices block (needs field_arr entries for LIST already created)
    list_data=bytearray()
    # map: which field_arr entries are lists -> set their dod now
    fa_i=0
    for s in flat:
        for lab,(ft,val) in s.fields.items():
            if ft==LIST:
                off=len(list_data)
                list_data.extend(struct.pack('<I',len(val)))
                for c in val: list_data.extend(struct.pack('<I',idmap[id(c)]))
                field_arr[fa_i][2]=off
            fa_i+=1

    # field indices block + struct dataoffsets
    field_idx_data=bytearray(); struct_recs=[]
    for si,s in enumerate(flat):
        fidxs=per_struct_fieldidx[si]; n=len(fidxs)
        if n==1: dod=fidxs[0]
        elif n>1:
            dod=len(field_idx_data)
            field_idx_data.extend(struct.pack('<%dI'%n,*fidxs))
        else: dod=0
        struct_recs.append((s.stype,dod,n))

    # labels block (16 bytes each)
    label_block=bytearray()
    for lab in labels:
        b=lab.encode('ascii')[:16]; label_block.extend(b+b'\x00'*(16-len(b)))

    # assemble
    HDR=56
    s_off=HDR
    f_off=s_off+len(struct_recs)*12
    l_off=f_off+len(field_arr)*12
    fd_off=l_off+len(label_block)
    fi_off=fd_off+len(field_data)
    li_off=fi_off+len(field_idx_data)
    out=bytearray()
    out+=ftype.encode('ascii')+ver.encode('ascii')
    out+=struct.pack('<12I',
        s_off,len(struct_recs), f_off,len(field_arr), l_off,len(labels),
        fd_off,len(field_data), fi_off,len(field_idx_data)//4, li_off,len(list_data)//4)
    for stype,dod,n in struct_recs: out+=struct.pack('<iII',stype,dod,n)
    for ft,li,dod in field_arr: out+=struct.pack('<III',ft,li,dod & 0xFFFFFFFF)
    out+=label_block; out+=field_data; out+=field_idx_data; out+=list_data
    if path: open(path,'wb').write(out)
    return bytes(out)

# ---------------- semantic compare ----------------
def equal(a,b,path=""):
    if a.stype!=b.stype: print("stype differ",path,a.stype,b.stype); return False
    if set(a.fields)!=set(b.fields):
        print("field set differ",path, set(a.fields)^set(b.fields)); return False
    for lab,(ft,val) in a.fields.items():
        ft2,val2=b.fields[lab]
        if ft!=ft2: print("type differ",path+"/"+lab,ft,ft2); return False
        if ft==STRUCT:
            if not equal(val,val2,path+"/"+lab): return False
        elif ft==LIST:
            if len(val)!=len(val2): print("list len differ",path+"/"+lab); return False
            for i,(x,y) in enumerate(zip(val,val2)):
                if not equal(x,y,"%s/%s[%d]"%(path,lab,i)): return False
        elif ft==FLOAT:
            if abs(val-val2)>1e-6: print("float differ",path+"/"+lab,val,val2); return False
        else:
            if val!=val2: print("value differ",path+"/"+lab,repr(val),repr(val2)); return False
    return True
