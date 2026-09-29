from pathlib import Path
import struct, hashlib, sys
sys.path.insert(0,'/mnt/data/edv9_work')
import inspect_autoit_lib as ia
from token_utils import line_slices, decode_line

ROOT=Path('/mnt/data/edv9_work')
BASE=ROOT/'EDv9_x64_KO_CLEAN_26v5.exe'
V4=ROOT/'EDv9_x64_Ko_26v4_hotfix.exe'
OUT=ROOT/'EDv9_x64_KO_CLEAN_26v5_DRIVERS_CLEANUP_TEST.exe'
MASK=0xffffffff

def sha(b): return hashlib.sha256(b).hexdigest().upper()
def align(x,a): return (x+a-1)//a*a

def get_resources(path):
    rs=ia.parse_pe(path)
    return {pp[1]:d for pp,d in rs if len(pp)>=2 and pp[0]==10 and isinstance(pp[1],str)}

def get_script_code(path):
    R=get_resources(path); res=R['SCRIPT']; dec,comp,codesz=ia.find_script(res)
    if comp!=0: raise ValueError('expected uncompressed active SCRIPT')
    if len(dec)!=codesz: raise ValueError('size mismatch')
    return res,dec

def build_script_resource(orig_resource,new_code):
    SIG=bytes.fromhex('A3484BBE986C4AA9994C530A86D6487D')
    pos=-1;scan=0
    while True:
        cand=orig_resource.find(SIG,scan)
        if cand<0:break
        if orig_resource[cand+0x10:cand+0x18]==b'AU3!EA06':pos=cand;break
        scan=cand+1
    if pos<0:raise ValueError('EA06 sig')
    p=pos+0x10+8+0x10; seen=0; target=None
    while p+8<=len(orig_resource):
        if ia.lame(orig_resource[p:p+4],0x18EE)!=b'FILE':raise ValueError(('FILE',hex(p)))
        p+=4;n=struct.unpack_from('<I',orig_resource,p)[0]^0xADBC;p+=4;p+=n*2
        n=struct.unpack_from('<I',orig_resource,p)[0]^0xF820;p+=4;p+=n*2
        meta=p;datasz=struct.unpack_from('<I',orig_resource,p+1)[0]^0x87BC;start=p+29
        seen+=1
        if seen==2:
            target=(meta,start,datasz);break
        p=start+datasz
    if not target:raise ValueError('SCRIPT entry')
    meta,start,oldsz=target
    prefix=bytearray(orig_resource[:start])
    prefix[meta]=0
    struct.pack_into('<I',prefix,meta+1,len(new_code)^0x87BC)
    struct.pack_into('<I',prefix,meta+5,len(new_code)^0x87BC)
    struct.pack_into('<I',prefix,meta+9,ia.crc(new_code)^0xA685)
    enc=ia.lame(new_code,0x2477)
    return bytes(prefix)+enc

def pe_info(b):
    pe=struct.unpack_from('<I',b,0x3c)[0];coff=pe+4;nsec=struct.unpack_from('<H',b,coff+2)[0];optsz=struct.unpack_from('<H',b,coff+16)[0];opt=coff+20
    magic=struct.unpack_from('<H',b,opt)[0];dd=opt+(112 if magic==0x20b else 96);st=opt+optsz
    sa=struct.unpack_from('<I',b,opt+32)[0];fa=struct.unpack_from('<I',b,opt+36)[0];secs=[]
    for i in range(nsec):
        o=st+i*40;name=b[o:o+8].split(b'\0')[0].decode('ascii','replace');vs,va,rs,raw=struct.unpack_from('<IIII',b,o+8);secs.append(dict(name=name,vs=vs,va=va,rs=rs,raw=raw,off=o))
    secdir=dd+8*4;cert_off,cert_sz=struct.unpack_from('<II',b,secdir);rr,rrsz=struct.unpack_from('<II',b,dd+16)
    return locals()

def resource_entries(b):
    d=pe_info(b);secs=d['secs'];rr=d['rr']
    def r2o(r):
        for s in secs:
            if s['va']<=r<s['va']+max(s['vs'],s['rs']):return s['raw']+(r-s['va'])
        raise ValueError(hex(r))
    base=r2o(rr)
    def u16(o):return struct.unpack_from('<H',b,o)[0]
    def u32(o):return struct.unpack_from('<I',b,o)[0]
    def nm(v):
        if not v&0x80000000:return v
        o=base+(v&0x7fffffff);n=u16(o);return b[o+2:o+2+2*n].decode('utf-16le')
    out={}
    def walk(rel,path):
        o=base+rel;cnt=u16(o+12)+u16(o+14)
        for i in range(cnt):
            eo=o+16+i*8;nv=u32(eo);cv=u32(eo+4);name=nm(nv);pp=path+[name]
            if cv&0x80000000:walk(cv&0x7fffffff,pp)
            else:
                de=base+(cv&0x7fffffff);out[tuple(pp)]=(de,u32(de),u32(de+4))
    walk(0,[]);return out,d

def pe_checksum(data,off):
    b=bytearray(data);b[off:off+4]=b'\0'*4;cs=0;i=0
    while i+1<len(b):
        cs=(cs+(b[i]|(b[i+1]<<8)))&0xffffffff;cs=(cs&0xffff)+(cs>>16);i+=2
    if i<len(b):cs=(cs+b[i])&0xffffffff;cs=(cs&0xffff)+(cs>>16)
    cs=(cs&0xffff)+(cs>>16);cs=cs+(cs>>16);return ((cs&0xffff)+len(b))&0xffffffff

def append_script_section(src,new_script):
    entries,d=resource_entries(src); core=bytearray(src);secs=d['secs'];last=max(secs,key=lambda s:s['raw']+s['rs']);raw_end=last['raw']+last['rs']
    if d['cert_off'] and d['cert_off']<raw_end:raise ValueError('cert overlap')
    overlay=src[raw_end:];core=bytearray(src[:raw_end]);raw=align(raw_end,d['fa']);va=align(max(s['va']+max(s['vs'],s['rs']) for s in secs),d['sa']);rs=align(len(new_script),d['fa']);vs=len(new_script)
    if raw>len(core):core.extend(b'\0'*(raw-len(core)))
    core.extend(new_script);core.extend(b'\0'*(rs-len(new_script)))
    if d['st']+(d['nsec']+1)*40>struct.unpack_from('<I',src,d['opt']+60)[0]:raise ValueError('no header room')
    o=d['st']+d['nsec']*40;core[o:o+8]=b'.kcln\0\0\0';struct.pack_into('<IIIIIIHHI',core,o+8,vs,va,rs,raw,0,0,0,0,0x40000040)
    struct.pack_into('<H',core,d['coff']+2,d['nsec']+1);struct.pack_into('<I',core,d['opt']+56,align(va+max(vs,rs),d['sa']));old_sid=struct.unpack_from('<I',src,d['opt']+8)[0];struct.pack_into('<I',core,d['opt']+8,old_sid+rs)
    key=(10,'SCRIPT',0)
    if key not in entries:raise ValueError('SCRIPT resource data entry missing')
    de,oldrva,oldsz=entries[key];struct.pack_into('<II',core,de,va,len(new_script))
    new_overlay=len(core);core.extend(overlay)
    if d['cert_off']:
        rel=d['cert_off']-raw_end;struct.pack_into('<II',core,d['secdir'],new_overlay+rel,d['cert_sz'])
    chk=d['opt']+64;struct.pack_into('<I',core,chk,0);struct.pack_into('<I',core,chk,pe_checksum(bytes(core),chk))
    return bytes(core)

# Extract active token streams.
base_res,base_code=get_script_code(BASE);v4_res,v4_code=get_script_code(V4)
base_total,base_sl=line_slices(base_code);v4_total,v4_sl=line_slices(v4_code)
assert base_total==24031 and v4_total==24027
# Proven fixed HOTFIX token lines. 68-69 = ownership flag + exit registration. 24019-24027 = cleanup Func incl canonical @ERROR.
pre=[v4_code[a:b] for a,b in (v4_sl[i-1] for i in (68,69))]
cleanup=[v4_code[a:b] for a,b in (v4_sl[i-1] for i in range(24019,24028))]
# Validate source line semantics without reconstructing anything.
assert '__SONG_DRIVERS_PREEXISTED' in decode_line(pre[0])[0]
assert '__SONG_FINAL_CLEANUP' in decode_line(pre[1])[0]
assert decode_line(cleanup[0])[0].startswith('__SONG_FINAL_CLEANUP')
assert any('@ERROR' in decode_line(x)[0] for x in cleanup)
assert not any('@error' in decode_line(x)[0] for x in cleanup)
# Insert immediately after 26v5 line 67, same semantic location used by 26v4 HOTFIX.
lines=[base_code[a:b] for a,b in base_sl]
new_lines=lines[:67]+pre+lines[67:]+cleanup
new_code=struct.pack('<I',len(new_lines))+b''.join(new_lines)
assert len(new_lines)==24042
# Verify inserted raw lines are exact byte copies from known working HOTFIX.
nt,nsl=line_slices(new_code);assert nt==24042
for off,src in [(68,pre[0]),(69,pre[1])]:
    a,b=nsl[off-1];assert new_code[a:b]==src
for j,src in enumerate(cleanup,24034): # 24031 base + 2 inserted => base ends 24033; cleanup starts 24034
    a,b=nsl[j-1];assert new_code[a:b]==src
# Build active SCRIPT and append redirect section.
new_sres=build_script_resource(base_res,new_code)
out=append_script_section(BASE.read_bytes(),new_sres);OUT.write_bytes(out)
print('BASE',sha(BASE.read_bytes()),BASE.stat().st_size)
print('OUT ',sha(out),len(out))
print('TOKEN',sha(new_code),len(new_code),'lines',nt)
print('SCRIPTRES',len(base_res),'->',len(new_sres))
for ln in [68,69,24034,24035,24036,24037,24038,24039,24040,24041,24042]:
    a,b=nsl[ln-1];print(ln,decode_line(new_code[a:b])[0],new_code[a:b][:16].hex())