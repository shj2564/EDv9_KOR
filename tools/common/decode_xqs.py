from pathlib import Path
import hashlib, re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

base=Path('/mnt/data/edv9_26v5_decoded')
R={n:(base/(n+'.bin')).read_bytes() for n in ['NWVBLDVM','OEVERVRW','PLAKRMHD','LABKLCBS']}

# CryptoAPI CryptDeriveKey behavior (PROV_RSA_AES), base hash MD5 (CALG_MD5)
def derive(password: bytes, alg):
    h=hashlib.md5(password).digest()
    if alg in ('aes128','aes192','aes256'):
        n={'aes128':16,'aes192':24,'aes256':32}[alg]
        # CryptoAPI CryptDeriveKey with AES and a non-SHA2 hash expands via ipad/opad even for AES-128.
        ipad=bytearray([0x36]*64); opad=bytearray([0x5c]*64)
        for i,b in enumerate(h): ipad[i]^=b; opad[i]^=b
        x=hashlib.md5(bytes(ipad)).digest()+hashlib.md5(bytes(opad)).digest()
        return x[:n]
    if alg=='rc4':
        return h[:16]
    raise ValueError(alg)

def rc4(data,key):
    S=list(range(256)); j=0
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])&255; S[i],S[j]=S[j],S[i]
    out=bytearray(); i=j=0
    for b in data:
        i=(i+1)&255; j=(j+S[i])&255; S[i],S[j]=S[j],S[i]
        k=S[(S[i]+S[j])&255]; out.append(b^k)
    return bytes(out)

def decrypt(data, password, alg):
    if isinstance(password,str): password=password.encode('cp1252') # all bootstrap passwords are ASCII here
    key=derive(password,alg)
    if alg=='rc4': return rc4(data,key)
    dec=Cipher(algorithms.AES(key),modes.CBC(b'\0'*16)).decryptor().update(data)
    # CryptDecrypt final=true: PKCS padding removed
    pad=dec[-1]
    if not (1<=pad<=16 and dec[-pad:]==bytes([pad])*pad):
        raise ValueError(f'bad pad {pad} alg={alg} len={len(data)} key={key.hex()} tail={dec[-32:].hex()}')
    return dec[:-pad]

members=[R['NWVBLDVM'],R['OEVERVRW'],R['PLAKRMHD']]
# TAJLVJAJZNJW: SHA1 of raw raid members, hex text, concatenated
loader_password=''.join(hashlib.sha1(x).hexdigest().upper()[:85] for x in members)
print('loader pw len',len(loader_password),loader_password)
loader_plain=decrypt(R['LABKLCBS'],loader_password,'aes256')
print('loader plain len',len(loader_plain),loader_plain[:200])
try: pswdict=loader_plain.decode('utf-8')
except Exception as e: print('loader utf8 fail',e); pswdict=loader_plain.decode('latin1')
print('PswDict len',len(pswdict),repr(pswdict[:300]))

def qou(idx):
    # StringMid is 1 based; char at idx determines output length, repeat/cycle dictionary if needed
    n=ord(pswdict[idx-1])
    out=''; pos=0
    while len(out)<n:
        take=min(n-len(out),len(pswdict)-pos)
        out += pswdict[pos:pos+take]
        pos += take
        if pos>=len(pswdict): pos=0
    return out

mdec=[]
for i,m in enumerate(members,1):
    pw=qou(i)
    d=decrypt(m,pw,'rc4')
    # BinaryToString(...,4)
    try: txt=d.decode('utf-8')
    except Exception as e:
        print('member utf8 fail',i,e,d[:100]); raise
    print('member',i,'pwlen',len(pw),'declen',len(d),'textlen',len(txt),'head',repr(txt[:80]),'tail',repr(txt[-100:]))
    mdec.append(txt)

def oddchars8(tail8):
    return ''.join(tail8[0::2])

data=[]; hashes=[]; psws=[]
for idx,txt in enumerate(mdec,1):
    # ODG: tail8, positions 1,3,5,7 -> hex decimal(?) Dec interprets hex string? AutoIt Dec('AB') => 171
    lmhex=oddchars8(txt[-8:]); L=int(lmhex,16)
    phex=txt[len(txt)-8-L:len(txt)-8]
    t=txt[:len(txt)-8-L]
    lhhex=oddchars8(t[-8:]); H=int(lhhex,16)
    htxt=t[len(t)-8-H:len(t)-8]
    datahex=t[:len(t)-8-H]
    # Binary('0x'+...) parses hex
    psw=bytes.fromhex(phex)
    dat=bytes.fromhex(datahex)
    # XKKADGRVUTZE rotates destinations: member i -> Data[i], Hash[i+1], Psw[i+2] (wrap 1..3)
    if not data:
        data=[None,None,None]; hashes=[None,None,None]; psws=[None,None,None]
    data[idx-1]=dat
    hash_idx=(idx % 3)          # 1->2(slot1), 2->3(slot2), 3->1(slot0)
    psw_idx=((idx+1) % 3)      # 1->3(slot2), 2->1(slot0), 3->2(slot1)
    hashes[hash_idx]=htxt
    psws[psw_idx]=psw
    print('ODG member',idx,'-> data',idx,'hash',hash_idx+1,'psw',psw_idx+1,'L',L,'H',H,'data',len(dat),'psw',len(psw))

# TDO hash transform -> Binary('0x'+transformed)
def tdo(h):
    # Exact AutoIt logic: take every other source character, two at a time,
    # interpret each pair as hex and Chr() it. This yields 43 chars from 172-char hash text.
    buw=''
    tmp=''
    for pos in range(0,len(h),2):
        tmp += h[pos]
        if len(tmp)==2:
            try: v=int(tmp,16)
            except: v=0
            buw += chr(v)
            tmp=''
    def adec(x):
        try: return int(x,16)
        except: return 0
    shift=adec(buw[-1:])
    hx=''
    # AutoIt: 1 to StringLen(buw)-1 (1-based)
    for pos in range(1,len(buw)):
        v=adec(buw[pos-1])
        if pos%2:
            v-=shift
            if v<0: v+=16
        else:
            v+=shift
            if v>15: v-=16
        hx += format(v,'X')[-1:]
    rot=adec(hx[:2])
    hx=hx[2:]
    if rot%2:
        hs=hx[-rot:] if rot else ''
        hx=hx[:-rot] if rot else hx
        hx=hs+hx
    else:
        hs=hx[:rot]
        hx=hx[rot:]+hs
    return bytes.fromhex(hx)

hashbin=[]
for i,h in enumerate(hashes,1):
    hb=tdo(h); hashbin.append(hb); print('hash',i,len(hb),hb.hex())

# YMED derives password text from triples in hex(Hashbin) excluding 0x
def ymed(hb):
    x=hb.hex().upper(); out=''
    pos=0
    while pos < len(x):
        chunk=x[pos:pos+3]
        if len(chunk)==3:
            start=int(chunk[:2],16); ln=int(chunk[2],16)
            if start>0 and ln>0:
                out += pswdict[start-1:start-1+ln]
        pos +=3
    return out[:128]

# JGUG decode encoded descriptors using PswDict; format comma list length.start? code SDJ=first, MES=second, substring(BPOL, MES, SDJ)
def jgug(enc):
    out=''
    for part in enc.split(','):
        bits=part.split('.')
        if len(bits)>=2:
            ln=int(bits[0]); start=int(bits[1])
            out += pswdict[start-1:start-1+ln]
    return out

pdata=[]
for i in range(3):
    p=ymed(hashbin[i]); print('ymed',i+1,len(p),repr(p))
    pp=decrypt(psws[i],p,'aes192').decode('utf-8')
    print('pswplain',i+1,len(pp),repr(pp[:200]))
    m=re.match(r'^(\d+)\.\d+,',pp)
    if not m: raise ValueError(('prefix',i,repr(pp[:100])))
    # AutoIt StringRegExp flag2 array: [full?, group?]. Code BLQ[1] likely captured digits. assume group 1
    L=int(m.group(1)); rest=pp[len(m.group(0)):]
    enc1=rest[:L]; enc2=rest[L+1:]
    p1=jgug(enc1); p2=jgug(enc2)
    print('data pw',i+1,len(p1),repr(p1[:80]),len(p2),repr(p2[:80]))
    d=decrypt(data[i],p2,'aes128')
    d=decrypt(d,p1,'aes256')
    hh=hashlib.sha1(d).digest()
    print('final data',i+1,len(d),'sha1',hh.hex(),'expected',hashbin[i].hex(),'match',hh==hashbin[i])
    if hh!=hashbin[i]: raise ValueError('hash mismatch')
    txt=d.decode('utf-8')
    pdata.append(txt)
    print('final text head',repr(txt[:100]),'tail',repr(txt[-100:]))

alltxt=''.join(pdata)
print('joined',len(alltxt),repr(alltxt[:100]))
delim=alltxt[:3]
# AutoIt StringSplit flag1 returns array [count, item1..]? QZQ index likely slot? The global QZQ used [4939], so include count at 0.
parts=alltxt[3:].split(delim)
print('delimiter',repr(delim),'parts',len(parts),'last',repr(parts[-1][:50]))
# build AutoIt-style array with [count] + entries; StringSplit omits? if no delimiter behavior. likely count index0
xqs=[len(parts)]+parts
(base/'xqs.json').write_text(__import__('json').dumps(xqs,ensure_ascii=False,indent=2),encoding='utf-8')
(base/'xqs_lines.txt').write_text('\n'.join(f'{i}\t{v}' for i,v in enumerate(xqs)),encoding='utf-8')
print('xqs max idx',len(xqs)-1,'count slot',xqs[0])
for needle in ['SoftInst','wget.exe','inst.cmd','inst.vbs','123.itsk.com','api.itsk.com','2345.com','hao.360.com','msedge.exe','PrefsLightweight','startup_urls','restore_on_startup','homepage','UnmountDrv']:
 hits=[(i,v) for i,v in enumerate(xqs) if isinstance(v,str) and needle.lower() in v.lower()]
 print('HIT',needle,len(hits),hits[:20])