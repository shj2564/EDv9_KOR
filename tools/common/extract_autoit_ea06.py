from pathlib import Path
import struct, hashlib, sys
MASK=0xffffffff
SIG=bytes.fromhex('A3484BBE986C4AA9994C530A86D6487D')

def rotl(x,n):
    return ((x<<n)&MASK) | ((x&MASK)>>(32-n))

class Lame:
    def __init__(self, seed):
        self.grp1=[0]*17
        for i in range(17):
            seed=(seed*0x53A9B4FB)&MASK
            seed=(1-seed)&MASK
            self.grp1[i]=seed
        self.c0=0; self.c1=10
        self.grp2=self.grp1.copy(); self.grp3=self.grp1.copy()
        for _ in range(9): self.fpusht()
    def fpusht(self):
        rolled=(rotl(self.grp1[self.c0],9)+rotl(self.grp1[self.c1],13))&MASK
        self.grp1[self.c0]=rolled
        if self.c0==0:self.c0=16
        else:self.c0-=1
        if self.c1==0:self.c1=16
        else:self.c1-=1
        lo=(rolled<<20)&MASK
        hi=((rolled>>12)|0x3FF00000)&MASK
        d=struct.unpack('<d',struct.pack('<II',lo,hi))[0]
        return d-1.0
    def getnext(self):
        self.fpusht()
        x=self.fpusht()*256.0
        return int(x) if int(x)<256 else 255

def lame_decrypt(data, seed):
    l=Lame(seed)
    return bytes((x ^ l.getnext()) for x in data)

def u32(b,o): return struct.unpack_from('<I',b,o)[0]

def crc_data(src):
    if not src:return 0
    ecx=0; esi=1
    for x in src:
        esi=(x+esi)%0xFFF1
        ecx=(ecx+esi)%0xFFF1
    return ((ecx<<16)+esi)&MASK

def find_script_payload(stream, verbose=True):
    pos=-1
    scan=0
    while True:
        cand=stream.find(SIG,scan)
        if cand<0: break
        if stream[cand+0x10:cand+0x18]==b'AU3!EA06':
            pos=cand; break
        scan=cand+1
    if pos<0: raise ValueError('AutoIt EA06 signature not found')
    p=pos+0x10
    p += 8+0x10
    entries=[]
    while p+8<=len(stream):
        dec=lame_decrypt(stream[p:p+4],0x18EE)
        if dec!=b'FILE':
            raise ValueError(f'FILE signature failed at {p:x}: {dec!r}')
        p+=4
        flagsz_chars=u32(stream,p)^0xADBC; p+=4
        flagsz=flagsz_chars*2
        flag_raw=lame_decrypt(stream[p:p+flagsz],0xB33F+flagsz_chars)
        p+=flagsz
        flag=flag_raw.decode('utf-16le','replace')
        path_chars=u32(stream,p)^0xF820; p+=4
        pathsz=path_chars*2
        path_raw=lame_decrypt(stream[p:p+pathsz],0xF479+path_chars)
        p+=pathsz
        path=path_raw.decode('utf-16le','replace')
        if p+29>len(stream): raise ValueError('truncated file metadata')
        comp=stream[p]
        datasz=u32(stream,p+1)^0x87BC
        codesz=u32(stream,p+5)^0x87BC
        crc=u32(stream,p+9)^0xA685
        meta_start=p
        data_start=p+1+4+4+4+0x10
        entries.append((flag,path,comp,datasz,codesz,crc,meta_start,data_start))
        if verbose:
            print(f'ENTRY flag={flag!r} path={path!r} comp={comp} datasz={datasz} codesz={codesz} crc={crc:08x} off={meta_start:x}')
        if flag == '>>>AUTOIT SCRIPT<<<':
            enc=stream[data_start:data_start+datasz]
            if len(enc)!=datasz: raise ValueError('truncated script data')
            decdata=lame_decrypt(enc,0x2477)
            got=crc_data(decdata)
            if got!=crc:
                raise ValueError(f'CRC mismatch {got:08x}!={crc:08x}')
            return entries, decdata, comp, codesz
        p=data_start+datasz
    raise ValueError('script entry not found')

class BitReader:
    def __init__(self,b):self.b=b;self.i=0;self.cur=0;self.bits=0
    def get(self,n):
        out=0
        for _ in range(n):
            if self.bits==0:
                if self.i+2>len(self.b): raise EOFError('bitstream EOF')
                self.cur=(self.b[self.i]<<8)|self.b[self.i+1]; self.i+=2; self.bits=16
            out=(out<<1)|((self.cur>>15)&1)
            self.cur=((self.cur<<1)&0xffff); self.bits-=1
        return out

def decompress_ea06(data):
    if data[:4]!=b'EA06': raise ValueError(f'bad compression signature {data[:4]!r}')
    usize=int.from_bytes(data[4:8],'big')
    br=BitReader(data[8:])
    out=bytearray()
    while len(out)<usize:
        if br.get(1)==1:
            out.append(br.get(8))
        else:
            bb=br.get(15); bs=br.get(2); add=0
            if bs==3:
                add=3; bs=br.get(3)
                if bs==7:
                    add=10; bs=br.get(5)
                    if bs==31:
                        add=41; bs=br.get(8)
                        if bs==255:
                            add=296; bs=br.get(8)
                            while bs==255:
                                add+=255; bs=br.get(8)
            length=bs+3+add
            src=len(out)-bb
            if src<0: raise ValueError(f'invalid backref {bb} at {len(out)}')
            for _ in range(length):
                out.append(out[src]); src+=1
                if len(out)>=usize: break
    return bytes(out)

def parse_tokens(code):
    if len(code)<4: raise ValueError('short token data')
    lines_total=u32(code,0); i=4; lines=[]; cur=[]; tokens=[]
    sym={0x40:',',0x41:'=',0x42:'>',0x43:'<',0x44:'<>',0x45:'>=',0x46:'<=',0x47:'(',0x48:')',0x49:'+',0x4a:'-',0x4b:'/',0x4c:'*',0x4d:'&',0x4e:'[',0x4f:']',0x50:'==',0x51:'^',0x52:'+=',0x53:'-=',0x54:'/= ',0x55:'*=',0x56:'&='}
    kind={0x30:'keyword',0x31:'?',0x32:'macro',0x33:'variable',0x34:'function',0x35:'object',0x36:'string',0x37:'?',0x38:'?',0x39:'?',0x3a:'?',0x3b:'?',0x3c:'?',0x3d:'?',0x3e:'?',0x3f:'?'}
    line_no=0
    while line_no<lines_total and i<len(code):
        op=code[i]
        if op==0x05:
            if i+5>len(code): break
            v=struct.unpack_from('<i',code,i+1)[0]; txt=str(v); i+=5
            cur.append(txt); tokens.append((line_no,op,'int32',txt))
        elif op==0x10:
            if i+9>len(code): break
            v=struct.unpack_from('<q',code,i+1)[0]; txt=hex(v & 0xffffffffffffffff); i+=9
            cur.append(txt); tokens.append((line_no,op,'int64',txt))
        elif op==0x20:
            if i+9>len(code): break
            v=struct.unpack_from('<d',code,i+1)[0]; txt=repr(v); i+=9
            cur.append(txt); tokens.append((line_no,op,'double',txt))
        elif 0x30<=op<=0x3f:
            if i+5>len(code): break
            n=u32(code,i+1); i+=5
            need=n*2
            if i+need>len(code): raise ValueError(f'truncated string token at {i:x} n={n}')
            chars=[]
            for j in range(n): chars.append(struct.unpack_from('<H',code,i+2*j)[0]^n)
            raw=struct.pack('<'+'H'*len(chars),*chars) if chars else b''
            txt=raw.decode('utf-16le','replace')
            i+=need
            disp=txt
            if op==0x33: disp='$'+txt
            elif op==0x32: disp='@'+txt
            elif op==0x36: disp='"'+txt.replace('"','""')+'"'
            cur.append(disp); tokens.append((line_no,op,kind.get(op,'?'),txt))
        elif op in sym:
            txt=sym[op].strip(); i+=1; cur.append(txt); tokens.append((line_no,op,'symbol',txt))
        elif op==0x7f:
            lines.append(' '.join(cur)); cur=[]; i+=1; line_no+=1
        else:
            # Match legacy decoder's width rules for numeric-ish token classes.
            start=i
            if op<=0x0f: i+=5
            elif op<=0x1f: i+=9
            elif op<=0x2f: i+=9
            else: i+=1
            tokens.append((line_no,op,'unknown',code[start:i].hex()))
    if cur: lines.append(' '.join(cur))
    return lines_total, lines, tokens, i

if __name__=='__main__':
    src=Path(sys.argv[1]).read_bytes()
    entries,decdata,comp,codesz=find_script_payload(src)
    print('decrypted data',len(decdata),'sha256',hashlib.sha256(decdata).hexdigest(),'head',decdata[:16])
    code=decompress_ea06(decdata) if comp==1 else decdata
    print('code',len(code),'expected',codesz,'sha256',hashlib.sha256(code).hexdigest(),'head',code[:16].hex())
    out=Path(sys.argv[2] if len(sys.argv)>2 else 'decoded')
    out.mkdir(parents=True,exist_ok=True)
    (out/'script.token.bin').write_bytes(code)
    total,lines,toks,end=parse_tokens(code)
    print('lines total',total,'parsed',len(lines),'tokens',len(toks),'end',end,'of',len(code))
    (out/'script.recovered.au3.txt').write_text('\n'.join(lines),encoding='utf-8')
    import json
    (out/'tokens.jsonl').write_text('\n'.join(json.dumps({'line':a,'op':b,'kind':c,'text':d},ensure_ascii=False) for a,b,c,d in toks),encoding='utf-8')