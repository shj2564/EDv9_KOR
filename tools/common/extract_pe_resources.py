from pathlib import Path
import struct,sys

def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def parse_pe(path,outdir=None):
    b=Path(path).read_bytes()
    if b[:2]!=b'MZ': raise ValueError('not MZ')
    peoff=u32(b,0x3c)
    if b[peoff:peoff+4]!=b'PE\0\0': raise ValueError('bad PE')
    coff=peoff+4
    nsec=u16(b,coff+2); optsz=u16(b,coff+16)
    opt=coff+20
    magic=u16(b,opt)
    if magic==0x20b: dd=opt+112
    elif magic==0x10b: dd=opt+96
    else: raise ValueError(hex(magic))
    rsrc_rva=u32(b,dd+8*2); rsrc_size=u32(b,dd+8*2+4)
    sec=opt+optsz
    sections=[]
    for i in range(nsec):
        o=sec+i*40
        name=b[o:o+8].split(b'\0')[0].decode('ascii','replace')
        vsize=u32(b,o+8); va=u32(b,o+12); rawsz=u32(b,o+16); raw=u32(b,o+20)
        sections.append((name,va,vsize,raw,rawsz))
    def rva2off(rva):
        for name,va,vs,raw,rs in sections:
            if va <= rva < va+max(vs,rs): return raw+(rva-va)
        raise ValueError(f'RVA {rva:x} not in sec')
    base=rva2off(rsrc_rva)
    def res_name(v):
        if not (v & 0x80000000): return v
        o=base+(v&0x7fffffff); n=u16(b,o); return b[o+2:o+2+2*n].decode('utf-16le','replace')
    results=[]
    def walk(rel,level,pathparts):
        o=base+rel
        named=u16(b,o+12); ids=u16(b,o+14); cnt=named+ids
        for i in range(cnt):
            eo=o+16+i*8
            nv=u32(b,eo); cv=u32(b,eo+4)
            name=res_name(nv)
            pp=pathparts+[name]
            if cv & 0x80000000:
                walk(cv&0x7fffffff,level+1,pp)
            else:
                do=base+(cv&0x7fffffff)
                data_rva=u32(b,do); sz=u32(b,do+4); cp=u32(b,do+8)
                off=rva2off(data_rva)
                results.append((pp,off,sz,cp,b[off:off+sz]))
    walk(0,0,[])
    if outdir:
        od=Path(outdir); od.mkdir(parents=True,exist_ok=True)
        for pp,off,sz,cp,data in results:
            if len(pp)>=2 and pp[0]==10 and isinstance(pp[1],str):
                (od/(pp[1]+'.bin')).write_bytes(data)
    return results,sections,(rsrc_rva,rsrc_size,base)

if __name__=='__main__':
    rs,secs,ri=parse_pe(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
    print('resource',ri)
    for pp,off,sz,cp,data in rs:
        if pp and (pp[0]==10 or pp[0]=='RCDATA'):
            print(pp,sz,hex(off))