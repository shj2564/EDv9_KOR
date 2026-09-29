from pathlib import Path
import struct, json, hashlib, re, math, copy
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import sys
sys.path.insert(0,'/mnt/data')
from extract_pe_resources import parse_pe
from extract_autoit_ea06 import (find_script_payload,decompress_ea06,parse_tokens,lame_decrypt,crc_data,u32)

ROOT=Path('/mnt/data/edv9_work')
V5=ROOT/'v5'/'EDv9_x64.exe'
MAN=Path('/mnt/data/EDv9_26v5_port_manifest.json')
V5DEC=Path('/mnt/data/edv9_26v5_decoded')

MASK=0xffffffff

def sha256(b): return hashlib.sha256(b).hexdigest()

def parse_line_slices(code: bytes):
    total=struct.unpack_from('<I',code,0)[0]
    i=4; starts=[]; ends=[]; line=0; start=i
    while line<total:
        op=code[i]
        if op==0x05: i+=5
        elif op==0x10 or op==0x20: i+=9
        elif 0x30<=op<=0x3f:
            n=struct.unpack_from('<I',code,i+1)[0]; i+=5+n*2
        elif 0x40<=op<=0x56: i+=1
        elif op==0x7f:
            i+=1; starts.append(start); ends.append(i); start=i; line+=1
        else:
            if op<=0x0f: i+=5
            elif op<=0x2f: i+=9
            else: i+=1
        if i>len(code): raise ValueError('token overrun')
    if i!=len(code):
        raise ValueError(f'token trailing bytes {len(code)-i}')
    return total,[(a,b) for a,b in zip(starts,ends)]

def patch_tokens(code: bytes, manifest: dict):
    total,slices=parse_line_slices(code)
    _,decoded,_t,_=parse_tokens(code)
    # Known-valid existing template lines.
    templates={}
    for mode,text in manifest['return_templates'].items():
        hits=[i for i,l in enumerate(decoded) if l==text]
        if not hits: raise ValueError(f'no template {mode}')
        idx=hits[0]
        a,b=slices[idx]
        templates[mode]=code[a:b]
    lines=[code[a:b] for a,b in slices]
    for p in manifest['code_patches']:
        if p['mode']=='BLANK_LINE':
            ln=p['v5_line']
            # Guard expected hash-mismatch return line.
            if 'RETURN $SAHBLBIS' not in decoded[ln-1]:
                raise ValueError((p['target_v5_function'],ln,decoded[ln-1]))
            lines[ln-1]=b'\x7f'
            continue
        s,e=p['v5_body_lines']
        mode=p['mode']
        lines[s-1]=templates[mode]
        for ln in range(s+1,e+1): lines[ln-1]=b'\x7f'
    out=struct.pack('<I',total)+b''.join(lines)
    # Post-parse and semantic checks.
    t2,l2,_tok,end=parse_tokens(out)
    assert t2==total and end==len(out) and len(l2)==total
    for p in manifest['code_patches']:
        if p['mode']=='BLANK_LINE':
            assert l2[p['v5_line']-1]==''
        else:
            s,e=p['v5_body_lines']; assert l2[s-1]==manifest['return_templates'][p['mode']]
            assert all(l2[i-1]=='' for i in range(s+1,e+1))
    return out,l2

# ----- XQS decode/rebuild -----
def derive(password: bytes, alg):
    if isinstance(password,str): password=password.encode('cp1252')
    h=hashlib.md5(password).digest()
    if alg in ('aes128','aes192','aes256'):
        n={'aes128':16,'aes192':24,'aes256':32}[alg]
        ipad=bytearray([0x36]*64); opad=bytearray([0x5c]*64)
        for i,b in enumerate(h): ipad[i]^=b; opad[i]^=b
        x=hashlib.md5(bytes(ipad)).digest()+hashlib.md5(bytes(opad)).digest()
        return x[:n]
    if alg=='rc4': return h[:16]
    raise ValueError(alg)

def rc4(data,key):
    S=list(range(256)); j=0
    for i in range(256):
        j=(j+S[i]+key[i%len(key)])&255; S[i],S[j]=S[j],S[i]
    out=bytearray(); i=j=0
    for b in data:
        i=(i+1)&255; j=(j+S[i])&255; S[i],S[j]=S[j],S[i]
        out.append(b^S[(S[i]+S[j])&255])
    return bytes(out)

def crypt(data,password,alg,encrypt=False):
    key=derive(password,alg)
    if alg=='rc4': return rc4(data,key)
    if encrypt:
        pad=16-(len(data)%16); src=data+bytes([pad])*pad
        enc=Cipher(algorithms.AES(key),modes.CBC(b'\0'*16)).encryptor()
        return enc.update(src)+enc.finalize()
    dec=Cipher(algorithms.AES(key),modes.CBC(b'\0'*16)).decryptor()
    out=dec.update(data)+dec.finalize(); pad=out[-1]
    if not (1<=pad<=16 and out[-pad:]==bytes([pad])*pad): raise ValueError('bad pad')
    return out[:-pad]

def tdo(h):
    buw=''; tmp=''
    for pos in range(0,len(h),2):
        tmp += h[pos]
        if len(tmp)==2:
            try:v=int(tmp,16)
            except:v=0
            buw+=chr(v);tmp=''
    def adec(x):
        try:return int(x,16)
        except:return 0
    shift=adec(buw[-1:]); hx=''
    for pos in range(1,len(buw)):
        v=adec(buw[pos-1])
        if pos%2:
            v-=shift
            if v<0:v+=16
        else:
            v+=shift
            if v>15:v-=16
        hx+=format(v,'X')[-1]
    rot=adec(hx[:2]); hx=hx[2:]
    if rot%2:
        hs=hx[-rot:] if rot else ''; hx=hx[:-rot] if rot else hx; hx=hs+hx
    else:
        hs=hx[:rot]; hx=hx[rot:]+hs
    return bytes.fromhex(hx)

def inv_tdo(digest: bytes):
    # Deterministic valid inverse: shift=0, rot=0.
    buw='00'+digest.hex().upper()+'0'
    assert len(buw)==43
    selected=''.join(f'{ord(c):02X}' for c in buw)
    assert len(selected)==86
    h=''.join(c+'0' for c in selected)
    assert len(h)==172 and tdo(h)==digest
    return h

def qou(pswdict,idx):
    n=ord(pswdict[idx-1]); out=''; pos=0
    while len(out)<n:
        take=min(n-len(out),len(pswdict)-pos); out+=pswdict[pos:pos+take];pos+=take
        if pos>=len(pswdict):pos=0
    return out

def ymed(pswdict,hb):
    x=hb.hex().upper();out=''
    for pos in range(0,len(x),3):
        chunk=x[pos:pos+3]
        if len(chunk)==3:
            start=int(chunk[:2],16);ln=int(chunk[2],16)
            if start>0 and ln>0: out+=pswdict[start-1:start-1+ln]
    return out[:128]

def jgug(pswdict,enc):
    out=''
    for part in enc.split(','):
        bits=part.split('.')
        if len(bits)>=2:
            ln=int(bits[0]);start=int(bits[1]);out+=pswdict[start-1:start-1+ln]
    return out

def lenmark(n):
    if not 0<=n<=0xffff: raise ValueError(n)
    s=f'{n:04X}'
    return ''.join(c+'0' for c in s)

def decode_xqs_resources(resources, names):
    r1,r2,r3,loader=[resources[n] for n in names]
    members=[r1,r2,r3]
    lp=''.join(hashlib.sha1(x).hexdigest().upper() for x in members)
    pswdict=crypt(loader,lp,'aes256',False).decode('utf-8')
    mdec=[crypt(m,qou(pswdict,i),'rc4',False).decode('utf-8') for i,m in enumerate(members,1)]
    data=[None]*3; hashes=[None]*3; psws=[None]*3
    for idx,txt in enumerate(mdec,1):
        L=int(''.join(txt[-8:][0::2]),16); phex=txt[len(txt)-8-L:len(txt)-8]; t=txt[:len(txt)-8-L]
        H=int(''.join(t[-8:][0::2]),16); htxt=t[len(t)-8-H:len(t)-8]; datahex=t[:len(t)-8-H]
        data[idx-1]=bytes.fromhex(datahex); hashes[idx%3]=htxt; psws[(idx+1)%3]=bytes.fromhex(phex)
    hbins=[tdo(x) for x in hashes]
    pp=[]; p1=[]; p2=[]; plains=[]
    for i in range(3):
        plainpp=crypt(psws[i],ymed(pswdict,hbins[i]),'aes192',False).decode('utf-8'); pp.append(plainpp)
        m=re.match(r'^(\d+)\.\d+,',plainpp); L=int(m.group(1)); rest=plainpp[len(m.group(0)):]
        e1=rest[:L];e2=rest[L+1:]; a=jgug(pswdict,e1);b=jgug(pswdict,e2);p1.append(a);p2.append(b)
        d=crypt(data[i],b,'aes128',False);d=crypt(d,a,'aes256',False)
        if hashlib.sha1(d).digest()!=hbins[i]: raise ValueError('data sha mismatch')
        plains.append(d)
    txts=[x.decode('utf-8') for x in plains]; alltxt=''.join(txts); delim=alltxt[:3]; parts=alltxt[3:].split(delim)
    xqs=[len(parts)]+parts
    return dict(pswdict=pswdict, pp=pp,p1=p1,p2=p2,plains=plains,delim=delim,xqs=xqs,hbins=hbins)

def split_stream_utf8(stream:str, delim:str):
    # split only at delimiter boundaries, roughly thirds
    btotal=len(stream.encode('utf-8')); targets=[btotal//3,2*btotal//3]
    positions=[]; search=3
    while True:
        p=stream.find(delim,search)
        if p<0:break
        positions.append(p+len(delim));search=p+len(delim)
    cuts=[]
    for t in targets:
        best=min(positions,key=lambda p:abs(len(stream[:p].encode('utf-8'))-t))
        if cuts and best<=cuts[-1]: best=next(p for p in positions if p>cuts[-1])
        cuts.append(best)
    return [stream[:cuts[0]].encode('utf-8'),stream[cuts[0]:cuts[1]].encode('utf-8'),stream[cuts[1]:].encode('utf-8')]

def rebuild_xqs(meta,new_xqs,names):
    delim=meta['delim']; stream=delim+delim.join(new_xqs[1:])
    blocks=split_stream_utf8(stream,delim)
    hbins=[hashlib.sha1(x).digest() for x in blocks]
    htxt=[inv_tdo(x) for x in hbins]
    pswenc=[]; dataenc=[]
    for i in range(3):
        pswenc.append(crypt(meta['pp'][i].encode('utf-8'),ymed(meta['pswdict'],hbins[i]),'aes192',True))
        c=crypt(blocks[i],meta['p1'][i],'aes256',True); c=crypt(c,meta['p2'][i],'aes128',True); dataenc.append(c)
    texts=[]
    for member_idx in range(3):
        hi=member_idx%3 # member1 stores hash slot2? Careful zero-based formula from decoder: hash_idx=(idx %3)
        # idx one-based => member_idx 0 -> hash slot1
        hi=(member_idx+1)%3
        pi=(member_idx+2)%3
        H=htxt[hi]; P=pswenc[pi].hex().upper(); D=dataenc[member_idx].hex().upper()
        texts.append(D+H+lenmark(len(H))+P+lenmark(len(P)))
    members=[]
    for i,t in enumerate(texts,1): members.append(crypt(t.encode('utf-8'),qou(meta['pswdict'],i),'rc4',True))
    lp=''.join(hashlib.sha1(x).hexdigest().upper() for x in members)
    loader=crypt(meta['pswdict'].encode('utf-8'),lp,'aes256',True)
    return {names[0]:members[0],names[1]:members[1],names[2]:members[2],names[3]:loader},blocks

# ----- AutoIt SCRIPT resource rebuild -----
def build_script_resource(orig_resource:bytes,new_code:bytes):
    # Locate EA06 stream then second FILE entry's metadata via same parser assumptions.
    SIG=bytes.fromhex('A3484BBE986C4AA9994C530A86D6487D')
    pos=-1;scan=0
    while True:
        cand=orig_resource.find(SIG,scan)
        if cand<0:break
        if orig_resource[cand+0x10:cand+0x18]==b'AU3!EA06':pos=cand;break
        scan=cand+1
    if pos<0:raise ValueError('sig')
    p=pos+0x10+8+0x10
    script_meta=None
    while p+8<=len(orig_resource):
        if lame_decrypt(orig_resource[p:p+4],0x18EE)!=b'FILE':raise ValueError('file sig')
        p+=4; fchars=struct.unpack_from('<I',orig_resource,p)[0]^0xADBC;p+=4;p+=fchars*2
        pchars=struct.unpack_from('<I',orig_resource,p)[0]^0xF820;p+=4;p+=pchars*2
        meta=p; comp=orig_resource[p]; datasz=struct.unpack_from('<I',orig_resource,p+1)[0]^0x87BC
        data_start=p+29
        # Decode flag by rewalking would be cumbersome; second entry is SCRIPT in these builds.
        if script_meta is None:
            script_meta='seen_first'
        else:
            script_meta=(meta,data_start,datasz);break
        p=data_start+datasz
    if not isinstance(script_meta,tuple):raise ValueError('script metadata')
    meta,data_start,oldsz=script_meta
    prefix=bytearray(orig_resource[:data_start])
    prefix[meta]=0
    struct.pack_into('<I',prefix,meta+1,len(new_code)^0x87BC)
    struct.pack_into('<I',prefix,meta+5,len(new_code)^0x87BC)
    struct.pack_into('<I',prefix,meta+9,crc_data(new_code)^0xA685)
    enc=lame_decrypt(new_code,0x2477)
    return bytes(prefix)+enc

# ----- PE resource redirect / append sections -----
def parse_pe_details(b:bytes):
    pe=struct.unpack_from('<I',b,0x3c)[0];coff=pe+4;nsec=struct.unpack_from('<H',b,coff+2)[0];optsz=struct.unpack_from('<H',b,coff+16)[0];opt=coff+20
    dd=opt+112 if struct.unpack_from('<H',b,opt)[0]==0x20b else opt+96
    sec_table=opt+optsz
    sa=struct.unpack_from('<I',b,opt+32)[0];fa=struct.unpack_from('<I',b,opt+36)[0]
    secs=[]
    for i in range(nsec):
        o=sec_table+i*40; name=b[o:o+8].split(b'\0')[0].decode('ascii','replace');vs,va,rs,raw=struct.unpack_from('<IIII',b,o+8)
        secs.append(dict(name=name,vs=vs,va=va,rs=rs,raw=raw,off=o))
    secdir_off=dd+8*4; cert_off,cert_sz=struct.unpack_from('<II',b,secdir_off)
    rsrc_rva,rsrc_sz=struct.unpack_from('<II',b,dd+8*2)
    return locals()

def resource_data_entries(b:bytes):
    d=parse_pe_details(b); secs=d['secs'];rr=d['rsrc_rva']
    def rva2off(rva):
        for s in secs:
            if s['va']<=rva<s['va']+max(s['vs'],s['rs']):return s['raw']+(rva-s['va'])
        raise ValueError(hex(rva))
    base=rva2off(rr)
    def u16(o):return struct.unpack_from('<H',b,o)[0]
    def u32_(o):return struct.unpack_from('<I',b,o)[0]
    def name(v):
        if not v&0x80000000:return v
        o=base+(v&0x7fffffff);n=u16(o);return b[o+2:o+2+2*n].decode('utf-16le')
    out={}
    def walk(rel,path):
        o=base+rel;cnt=u16(o+12)+u16(o+14)
        for i in range(cnt):
            eo=o+16+i*8;nv=u32_(eo);cv=u32_(eo+4);nm=name(nv);pp=path+[nm]
            if cv&0x80000000:walk(cv&0x7fffffff,pp)
            else:
                de=base+(cv&0x7fffffff);rva=u32_(de);sz=u32_(de+4);out[tuple(pp)]=(de,rva,sz)
    walk(0,[]);return out,d

def align(x,a):return (x+a-1)//a*a

def pe_checksum(data:bytes,checksum_off:int):
    # PE checksum per MapFileAndCheckSum semantics.
    b=bytearray(data); b[checksum_off:checksum_off+4]=b'\0\0\0\0'
    csum=0; n=len(b); i=0
    while i+1<n:
        w=b[i]|(b[i+1]<<8); csum=(csum+w)&0xffffffff; csum=(csum&0xffff)+(csum>>16);i+=2
    if i<n:
        csum=(csum+b[i])&0xffffffff;csum=(csum&0xffff)+(csum>>16)
    csum=(csum&0xffff)+(csum>>16);csum=csum+(csum>>16);csum=(csum&0xffff)+n
    return csum&0xffffffff

def append_resources_pe(src:bytes, script_res:bytes, xres:dict, script_name='SCRIPT'):
    entries,d=resource_data_entries(src); b=bytearray(src)
    pe=d['pe'];coff=d['coff'];opt=d['opt'];dd=d['dd'];sec_table=d['sec_table'];nsec=d['nsec'];sa=d['sa'];fa=d['fa'];secs=d['secs'];cert_off=d['cert_off'];cert_sz=d['cert_sz'];secdir_off=d['secdir_off']
    # Verify cert/overlay is at EOF and preserve bytes after last section.
    last=max(secs,key=lambda s:s['raw']+s['rs']); raw_end=last['raw']+last['rs']
    if cert_off and cert_off<raw_end: raise ValueError('cert overlaps sections')
    overlay=src[raw_end:]
    core=bytearray(src[:raw_end])
    # Two new sections, packing SCRIPT and XQS resources.
    payloads=[]
    for secname,items in [('.kscr',[(script_name,script_res)]),('.kres',list(xres.items()))]:
        blob=bytearray(); loc={}
        for nm,dat in items:
            off=align(len(blob),16); blob.extend(b'\0'*(off-len(blob)));loc[nm]=(off,len(dat));blob.extend(dat)
        payloads.append((secname,bytes(blob),loc))
    newsecs=[]; current_raw=align(raw_end,fa); current_va=align(max(s['va']+max(s['vs'],s['rs']) for s in secs),sa)
    if current_raw>len(core): core.extend(b'\0'*(current_raw-len(core)))
    for secname,blob,loc in payloads:
        raw=current_raw; va=current_va; rs=align(len(blob),fa);vs=len(blob)
        core.extend(blob);core.extend(b'\0'*(rs-len(blob)))
        newsecs.append(dict(name=secname,raw=raw,va=va,rs=rs,vs=vs,loc=loc))
        current_raw=raw+rs;current_va=align(va+max(vs,rs),sa)
    # Update resource data entries to new RVAs/sizes.
    targets={script_name:(newsecs[0],newsecs[0]['loc'][script_name])}
    for nm in xres:targets[nm]=(newsecs[1],newsecs[1]['loc'][nm])
    for nm,(s,(lo,sz)) in targets.items():
        key=(10,nm,0)
        if key not in entries: raise ValueError(f'missing resource {key}')
        de,oldrva,oldsz=entries[key]
        struct.pack_into('<II',core,de,s['va']+lo,sz)
    # Add section headers.
    if sec_table+(nsec+len(newsecs))*40 > struct.unpack_from('<I',src,opt+60)[0]: raise ValueError('no header room')
    for j,s in enumerate(newsecs):
        o=sec_table+(nsec+j)*40;name=s['name'].encode('ascii')[:8].ljust(8,b'\0')
        core[o:o+8]=name;struct.pack_into('<IIIIIIHHI',core,o+8,s['vs'],s['va'],s['rs'],s['raw'],0,0,0,0,0x40000040)
    struct.pack_into('<H',core,coff+2,nsec+len(newsecs))
    struct.pack_into('<I',core,opt+56,current_va) # SizeOfImage
    # SizeOfInitializedData += new section raw sizes
    old_sid=struct.unpack_from('<I',src,opt+8)[0];struct.pack_into('<I',core,opt+8,old_sid+sum(s['rs'] for s in newsecs))
    # Re-append overlay/certificate, updating security dir file offset by delta.
    new_overlay_off=len(core)
    core.extend(overlay)
    if cert_off:
        cert_rel=cert_off-raw_end; struct.pack_into('<II',core,secdir_off,new_overlay_off+cert_rel,cert_sz)
    # checksum
    chkoff=opt+64;struct.pack_into('<I',core,chkoff,0);chk=pe_checksum(bytes(core),chkoff);struct.pack_into('<I',core,chkoff,chk)
    return bytes(core),newsecs

def main():
    src=V5.read_bytes(); manifest=json.loads(MAN.read_text('utf-8'))
    assert sha256(src)==manifest['target']['original_exe_sha256']
    # Extract original resources according to PE directory.
    rs,_,_=parse_pe(V5); resources={pp[1]:dat for pp,off,sz,cp,dat in rs if len(pp)>=2 and pp[0]==10 and isinstance(pp[1],str)}
    xnames=['NWVBLDVM','OEVERVRW','PLAKRMHD','LABKLCBS']
    meta=decode_xqs_resources(resources,xnames)
    assert len(meta['xqs'])==4941
    # Apply XQS manifest with source-value SHA guards.
    xqs=list(meta['xqs'])
    for p in manifest['xqs_patches']:
        idx=p['v5_index']; old=xqs[idx]; h=hashlib.sha256(old.encode('utf-8')).hexdigest()
        if h!=p['source_sha256']: raise ValueError(f'XQS guard {idx}: {h}!={p["source_sha256"]}')
        xqs[idx]=p['target']
    xres,blocks=rebuild_xqs(meta,xqs,xnames)
    # immediate decrypt roundtrip of rebuilt resources
    meta2=decode_xqs_resources(xres,xnames)
    if meta2['xqs']!=xqs: raise ValueError('XQS roundtrip mismatch')
    # Token stream patch from active SCRIPT resource.
    sres=resources['SCRIPT']; entries,dec,comp,codesz=find_script_payload(sres,verbose=False); code=decompress_ea06(dec) if comp==1 else dec
    assert sha256(code)==manifest['target']['original_token_sha256']
    newcode,newlines=patch_tokens(code,manifest)
    new_sres=build_script_resource(sres,newcode)
    # validate script resource roundtrip
    _e,d2,c2,z2=find_script_payload(new_sres,verbose=False); code2=decompress_ea06(d2) if c2==1 else d2
    assert code2==newcode and c2==0 and z2==len(newcode)
    # Build final PE with redirected resources.
    out,newsecs=append_resources_pe(src,new_sres,xres)
    outp=ROOT/'EDv9_x64_KO_CLEAN_26v5.exe';outp.write_bytes(out)
    print('OUTPUT',outp,len(out),sha256(out))
    print('TOKEN',len(code),'->',len(newcode),sha256(newcode))
    print('SCRIPTRES',len(sres),'->',len(new_sres))
    print('XRES',[(k,len(v)) for k,v in xres.items()])
    print('BLOCKS',[len(x) for x in blocks])
    print('SECTIONS',newsecs)

if __name__=='__main__': main()