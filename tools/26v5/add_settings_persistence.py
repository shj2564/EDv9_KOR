from pathlib import Path
import struct, hashlib, sys

BASE=Path(sys.argv[1] if len(sys.argv)>1 else 'EDv9_x64_KO_CLEAN.exe')
OUT=Path(sys.argv[2] if len(sys.argv)>2 else 'EDv9_x64_KO_CLEAN_SETTINGS_SAVE_TEST.exe')
EXPECTED_BASE='955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713'
EXPECTED_TOKEN='C2FE0C9D5FBA4A43697A81798710C0A164E5EB1BEB62E66B494EBCB15A9F6861'
MASK=0xffffffff
SIG=bytes.fromhex('A3484BBE986C4AA9994C530A86D6487D')

def sha(b): return hashlib.sha256(b).hexdigest().upper()
def rotl(x,n): return ((x<<n)&MASK)|((x&MASK)>>(32-n))
class Lame:
    def __init__(self,seed):
        self.grp1=[0]*17
        for i in range(17):
            seed=(seed*0x53A9B4FB)&MASK; seed=(1-seed)&MASK; self.grp1[i]=seed
        self.c0=0; self.c1=10
        for _ in range(9): self.fpusht()
    def fpusht(self):
        rolled=(rotl(self.grp1[self.c0],9)+rotl(self.grp1[self.c1],13))&MASK
        self.grp1[self.c0]=rolled
        self.c0=16 if self.c0==0 else self.c0-1
        self.c1=16 if self.c1==0 else self.c1-1
        lo=(rolled<<20)&MASK; hi=((rolled>>12)|0x3FF00000)&MASK
        return struct.unpack('<d',struct.pack('<II',lo,hi))[0]-1.0
    def getnext(self):
        self.fpusht(); x=self.fpusht()*256.0
        return int(x) if int(x)<256 else 255
def lame(data,seed):
    l=Lame(seed); return bytes(x^l.getnext() for x in data)
def crc_data(src):
    if not src:return 0
    ecx=0;esi=1
    for x in src:
        esi=(x+esi)%0xFFF1; ecx=(ecx+esi)%0xFFF1
    return ((ecx<<16)+esi)&MASK

def line_slices(code):
    total=struct.unpack_from('<I',code,0)[0];i=4;start=i;out=[]
    while len(out)<total:
        op=code[i]
        if op==0x05:i+=5
        elif op in (0x10,0x20):i+=9
        elif 0x30<=op<=0x3f:
            n=struct.unpack_from('<I',code,i+1)[0];i+=5+n*2
        elif 0x40<=op<=0x56:i+=1
        elif op==0x7f:
            i+=1;out.append((start,i));start=i
        else:
            if op<=0x0f:i+=5
            elif op<=0x2f:i+=9
            else:i+=1
        if i>len(code): raise ValueError('token overrun')
    if i!=len(code): raise ValueError(f'token trailing {len(code)-i}')
    return total,out

sym={',':0x40,'=':0x41,'>':0x42,'<':0x43,'<>':0x44,'>=':0x45,'<=':0x46,'(':0x47,')':0x48,'+':0x49,'-':0x4a,'/':0x4b,'*':0x4c,'&':0x4d,'[':0x4e,']':0x4f,'==':0x50,'^':0x51,'+=':0x52,'-=':0x53,'/=':0x54,'*=':0x55,'&=':0x56}
def st(op,s):
    n=len(s); raw=s.encode('utf-16le'); vals=list(struct.unpack('<'+'H'*n,raw)) if n else []
    enc=struct.pack('<'+'H'*n,*[(v^n)&0xffff for v in vals]) if vals else b''
    return bytes([op])+struct.pack('<I',n)+enc
def kw(s):return st(0x30,s.upper())
def mac(s):return st(0x32,s.upper())
def var(s):return st(0x33,s.lstrip('$'))
def fn(s):return st(0x34,s)
def string(s):return st(0x36,s)
def i32(n):return bytes([0x05])+struct.pack('<i',n)
def sy(s):return bytes([sym[s]])
def line(*parts):return b''.join(parts)+b'\x7f'

def decode_line(raw):
    i=0;out=[]
    while i<len(raw):
        op=raw[i]
        if op==0x7f:break
        if op==0x05:
            out.append(str(struct.unpack_from('<i',raw,i+1)[0]));i+=5;continue
        if 0x30<=op<=0x3f:
            n=struct.unpack_from('<I',raw,i+1)[0]
            chars=[struct.unpack_from('<H',raw,i+5+2*j)[0]^n for j in range(n)]
            txt=(struct.pack('<'+'H'*n,*chars).decode('utf-16le') if n else '')
            i+=5+n*2
            if op==0x33:txt='$'+txt
            elif op==0x32:txt='@'+txt
            elif op==0x36:txt='"'+txt+'"'
            out.append(txt);continue
        if op in sym.values():
            out.append(next(k for k,v in sym.items() if v==op));i+=1;continue
        if op<=0x0f:i+=5
        elif op<=0x2f:i+=9
        else:i+=1
    return ' '.join(out)

def pe_info(b):
    pe=struct.unpack_from('<I',b,0x3c)[0];coff=pe+4;nsec=struct.unpack_from('<H',b,coff+2)[0]
    optsz=struct.unpack_from('<H',b,coff+16)[0];opt=coff+20
    magic=struct.unpack_from('<H',b,opt)[0];dd=opt+(112 if magic==0x20b else 96);st=opt+optsz
    sa=struct.unpack_from('<I',b,opt+32)[0];fa=struct.unpack_from('<I',b,opt+36)[0];secs=[]
    for j in range(nsec):
        o=st+j*40;name=b[o:o+8].split(b'\0')[0].decode('ascii','replace')
        vs,va,rs,raw=struct.unpack_from('<IIII',b,o+8)
        secs.append(dict(name=name,vs=vs,va=va,rs=rs,raw=raw,off=o))
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
        for j in range(cnt):
            eo=o+16+j*8;nv=u32(eo);cv=u32(eo+4);name=nm(nv);pp=path+[name]
            if cv&0x80000000:walk(cv&0x7fffffff,pp)
            else:
                de=base+(cv&0x7fffffff);out[tuple(pp)]=(de,u32(de),u32(de+4))
    walk(0,[])
    return out,d,r2o

def get_active_script_resource(src):
    entries,d,r2o=resource_entries(src); key=(10,'SCRIPT',0)
    if key not in entries:raise ValueError('SCRIPT RCDATA missing')
    de,rva,sz=entries[key];off=r2o(rva)
    return src[off:off+sz],entries,d

def get_script_code(resource):
    pos=-1;scan=0
    while True:
        cand=resource.find(SIG,scan)
        if cand<0:break
        if resource[cand+0x10:cand+0x18]==b'AU3!EA06':pos=cand;break
        scan=cand+1
    if pos<0:raise ValueError('EA06 sig')
    p=pos+0x10+8+0x10
    while p+8<=len(resource):
        if lame(resource[p:p+4],0x18EE)!=b'FILE':raise ValueError('FILE')
        p+=4;fc=struct.unpack_from('<I',resource,p)[0]^0xADBC;p+=4
        flag=lame(resource[p:p+fc*2],0xB33F+fc).decode('utf-16le');p+=fc*2
        pc=struct.unpack_from('<I',resource,p)[0]^0xF820;p+=4;p+=pc*2
        comp=resource[p];datasz=struct.unpack_from('<I',resource,p+1)[0]^0x87BC
        codesz=struct.unpack_from('<I',resource,p+5)[0]^0x87BC
        crc=struct.unpack_from('<I',resource,p+9)[0]^0xA685;start=p+29
        if flag=='>>>AUTOIT SCRIPT<<<':
            dec=lame(resource[start:start+datasz],0x2477)
            if crc_data(dec)!=crc:raise ValueError('CRC')
            if comp!=0:raise ValueError('active script expected uncompressed')
            if len(dec)!=codesz:raise ValueError('codesz')
            return dec
        p=start+datasz
    raise ValueError('SCRIPT entry')

def build_script_resource(orig_resource,new_code):
    pos=-1;scan=0
    while True:
        cand=orig_resource.find(SIG,scan)
        if cand<0:break
        if orig_resource[cand+0x10:cand+0x18]==b'AU3!EA06':pos=cand;break
        scan=cand+1
    if pos<0:raise ValueError('EA06 sig')
    p=pos+0x10+8+0x10
    while p+8<=len(orig_resource):
        if lame(orig_resource[p:p+4],0x18EE)!=b'FILE':raise ValueError('FILE')
        p+=4;fc=struct.unpack_from('<I',orig_resource,p)[0]^0xADBC;p+=4
        flag=lame(orig_resource[p:p+fc*2],0xB33F+fc).decode('utf-16le');p+=fc*2
        pc=struct.unpack_from('<I',orig_resource,p)[0]^0xF820;p+=4;p+=pc*2
        meta=p;datasz=struct.unpack_from('<I',orig_resource,p+1)[0]^0x87BC;start=p+29
        if flag=='>>>AUTOIT SCRIPT<<<':
            prefix=bytearray(orig_resource[:start]);prefix[meta]=0
            struct.pack_into('<I',prefix,meta+1,len(new_code)^0x87BC)
            struct.pack_into('<I',prefix,meta+5,len(new_code)^0x87BC)
            struct.pack_into('<I',prefix,meta+9,crc_data(new_code)^0xA685)
            return bytes(prefix)+lame(new_code,0x2477)
        p=start+datasz
    raise ValueError('script entry')

def align(x,a):return (x+a-1)//a*a
def pe_checksum(data,off):
    b=bytearray(data);b[off:off+4]=b'\0'*4;cs=0;i=0
    while i+1<len(b):
        cs=(cs+(b[i]|(b[i+1]<<8)))&0xffffffff;cs=(cs&0xffff)+(cs>>16);i+=2
    if i<len(b):cs=(cs+b[i])&0xffffffff;cs=(cs&0xffff)+(cs>>16)
    cs=(cs&0xffff)+(cs>>16);cs=cs+(cs>>16)
    return ((cs&0xffff)+len(b))&0xffffffff

def append_script_section(src,new_script):
    entries,d,_=resource_entries(src);secs=d['secs']
    last=max(secs,key=lambda s:s['raw']+s['rs']);raw_end=last['raw']+last['rs']
    if d['cert_off'] and d['cert_off']<raw_end:raise ValueError('cert overlap')
    overlay=src[raw_end:];core=bytearray(src[:raw_end])
    raw=align(raw_end,d['fa']);va=align(max(s['va']+max(s['vs'],s['rs']) for s in secs),d['sa'])
    rs=align(len(new_script),d['fa']);vs=len(new_script)
    if raw>len(core):core.extend(b'\0'*(raw-len(core)))
    core.extend(new_script);core.extend(b'\0'*(rs-len(new_script)))
    if d['st']+(d['nsec']+1)*40>struct.unpack_from('<I',src,d['opt']+60)[0]:raise ValueError('no header room')
    o=d['st']+d['nsec']*40;core[o:o+8]=b'.kpref\0\0'
    struct.pack_into('<IIIIIIHHI',core,o+8,vs,va,rs,raw,0,0,0,0,0x40000040)
    struct.pack_into('<H',core,d['coff']+2,d['nsec']+1)
    struct.pack_into('<I',core,d['opt']+56,align(va+max(vs,rs),d['sa']))
    old_sid=struct.unpack_from('<I',src,d['opt']+8)[0]
    struct.pack_into('<I',core,d['opt']+8,old_sid+rs)
    de,_,_=entries[(10,'SCRIPT',0)]
    struct.pack_into('<II',core,de,va,len(new_script))
    new_overlay=len(core);core.extend(overlay)
    if d['cert_off']:
        rel=d['cert_off']-raw_end
        struct.pack_into('<II',core,d['secdir'],new_overlay+rel,d['cert_sz'])
    chk=d['opt']+64;struct.pack_into('<I',core,chk,0)
    struct.pack_into('<I',core,chk,pe_checksum(bytes(core),chk))
    return bytes(core)

KEY='HKCU\\Software\\SoNG\\EDv9_KOR'
def mapcall(idx,args):
    parts=[var('SAHBLBIS'),sy('['),i32(idx),sy(']'),sy('(')]
    for j,a in enumerate(args):
        if j:parts.append(sy(','))
        parts.extend(a if isinstance(a,list) else [a])
    parts.append(sy(')'))
    return parts
def vexpr(name): return [var(name)]
def sexpr(s): return [string(s)]
def mapexpr(idx,args): return mapcall(idx,args)

load=[
line(kw('FUNC'),fn('__SONG_PREFS_LOAD'),sy('('),kw('BYREF'),var('SONG_EXTRACT'),sy(','),kw('BYREF'),var('SONG_REBOOT'),sy(')')),
line(kw('LOCAL'),var('SONG_V')),
line(kw('IF'),var('SONG_EXTRACT'),sy('='),i32(0),kw('THEN')),
line(var('SONG_V'),sy('='),*mapcall(164,[sexpr(KEY),sexpr('Extract')])),
line(kw('IF'),mac('ERROR'),sy('='),i32(0),kw('THEN')),
line(kw('IF'),var('SONG_V'),sy('='),i32(1),kw('THEN')),
line(var('SONG_EXTRACT'),sy('='),i32(1)),
line(kw('ENDIF')),line(kw('ENDIF')),line(kw('ENDIF')),
line(kw('IF'),var('SONG_REBOOT'),sy('<>'),i32(0),kw('THEN')),
line(var('SONG_V'),sy('='),*mapcall(164,[sexpr(KEY),sexpr('NeedReboot')])),
line(kw('IF'),mac('ERROR'),sy('='),i32(0),kw('THEN')),
line(kw('IF'),var('SONG_V'),sy('='),i32(0),kw('THEN')),
line(var('SONG_REBOOT'),sy('='),i32(0)),
line(kw('ENDIF')),line(kw('ENDIF')),line(kw('ENDIF')),
line(kw('RETURN')),line(kw('ENDFUNC'))
]
save=[
line(kw('FUNC'),fn('__SONG_PREFS_SAVE'),sy('('),var('SONG_EXTRACT'),sy(','),var('SONG_REBOOT'),sy(')')),
line(*mapcall(1120,[sexpr(KEY),sexpr('Extract'),sexpr('REG_DWORD'),mapexpr(176,[vexpr('SONG_EXTRACT')])])),
line(*mapcall(1120,[sexpr(KEY),sexpr('NeedReboot'),sexpr('REG_DWORD'),mapexpr(176,[vexpr('SONG_REBOOT')])])),
line(kw('RETURN')),line(kw('ENDFUNC'))
]
load_call=line(fn('__SONG_PREFS_LOAD'),sy('('),var('DLNLABLC'),sy(','),var('MSGJVIQH'),sy(')'))
save_call=line(fn('__SONG_PREFS_SAVE'),sy('('),var('DLNLABLC'),sy(','),var('MSGJVIQH'),sy(')'))

src=BASE.read_bytes()
if sha(src)!=EXPECTED_BASE: raise SystemExit(f'BASE hash mismatch {sha(src)}')
res,_,_=get_active_script_resource(src);code=get_script_code(res)
if sha(code)!=EXPECTED_TOKEN: raise SystemExit(f'TOKEN hash mismatch {sha(code)}')
total,sl=line_slices(code)
if total!=24042: raise SystemExit(f'Unexpected token lines: {total}')
lines=[code[a:b] for a,b in sl]
def dl(n): return decode_line(lines[n-1])
assert dl(22967).startswith('LOCAL $DLNLABLC =')
assert dl(22969).startswith('LOCAL $MSGJVIQH =')
assert dl(23043).startswith('$SAHBLBIS [ 683 ]')
assert dl(23044)=='IF NOT ( @ERROR ) THEN'

lines2=lines[:22969]+[load_call]+lines[22969:]
lines2=lines2[:23045]+[save_call]+lines2[23045:]
lines2 += load+save
newcode=struct.pack('<I',len(lines2))+b''.join(lines2)
nt,_=line_slices(newcode)
assert nt==24069
assert lines2[22969]==load_call and lines2[23045]==save_call
filtered=[x for i,x in enumerate(lines2[:len(lines)+2]) if i not in (22969,23045)]
assert filtered==lines

newres=build_script_resource(res,newcode)
out=append_script_section(src,newres)
OUT.write_bytes(out)
print('BASE_SHA',sha(src),len(src))
print('OUT_SHA',sha(out),len(out))
print('TOKEN_SHA',sha(newcode),len(newcode),'LINES',nt)
