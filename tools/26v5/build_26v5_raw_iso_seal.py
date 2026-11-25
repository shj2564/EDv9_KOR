#!/usr/bin/env python3
"""EDv9 26v5 one-EXE native popups + raw ISO SHA256 self-seal build.

Build only in isolated staging. Does not touch verified source EXE/ISO.
Workflow:
  build       - append original 26v4 popups, guard code and empty seal section
  seal <iso>  - seal an oscdimg-built UDF 1.02 ISO in-place (same file size)
  verify <iso> - verify normalized full-media SHA256 and stage EXE equality
"""
from pathlib import Path
import hashlib, struct, sys, json, mmap, os, types
ROOT = Path(r"D:\SoNG-HoME_Admin\SoNG_Admin\Downloads\EDv9_26v5_ISO_GUARD_WORK_20261125")
sys.path.insert(0,str(ROOT))
from extract_pe_resources import parse_pe
from extract_autoit_ea06 import find_script_payload,parse_tokens,decompress_ea06

BASE = ROOT/"EDv9_x64_KO_CLEAN_BASE.exe"
V4 = ROOT/"EDv9_x64_Ko.exe"
FRAG = ROOT/"edv9_native_iso_guard_fragment.exe"
STAGE = ROOT/"ISO_STAGE"/"EDv9_x64_KO_CLEAN.exe"
OUT = ROOT/"EDv9_x64_KO_CLEAN_GUARDED_UNSEALED.exe"
V5_SHA = "12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA"
V4_SHA = "2A36250601AB18CCC62B563744A69715F6D10C37B5B1B9CEB7E9E9AD96710A52"
PREFIX=b"EDV9_ISO_SEAL_V1|O="
MARKER=PREFIX+b"0"*16+b"|S="+b"0"*16+b"|H="+b"0"*64+b"|END"
HASH_BEGIN=MARKER.index(b"|H=")+3
OFF_BEGIN=MARKER.index(b"|O=")+3
SIZE_BEGIN=MARKER.index(b"|S=")+3
FILE_ALIGN_MARKER=16

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb",buffering=0) as f:
        for block in iter(lambda:f.read(8*1024*1024),b""):
            h.update(block)
    return h.hexdigest().upper()

def lib():
    # Reuse existing native EA06 token and PE-resource routines from the
    # verified SettingsSave FINAL build, without invoking its build main.
    script=(ROOT/"add_settings_persistence.py").read_text(encoding="utf-8-sig")
    anchor="\nsrc=BASE.read_bytes()"
    if anchor not in script:raise RuntimeError("Baseline library anchor absent")
    md=types.ModuleType("edv9lib")
    old=list(sys.argv)
    sys.argv=[str(ROOT/"add_settings_persistence.py"),str(BASE)]
    try:exec(compile(script.split(anchor)[0],str(ROOT/"add_settings_persistence.py"),"exec"),md.__dict__)
    finally:sys.argv=old
    return md

def script_code(path,L):
    rs,sections,_=parse_pe(path)
    p=[x[-1] for x in rs if len(x[0])>=2 and x[0][0]==10 and x[0][1]=="SCRIPT"]
    if len(p)!=1:raise RuntimeError("Missing SCRIPT resource")
    _files,dec,compressed,code_size=find_script_payload(p[0],verbose=False)
    if compressed:dec=decompress_ea06(dec)
    if code_size!=len(dec):raise RuntimeError("SCRIPT length mismatch")
    total,spans=L.line_slices(dec)
    if len(spans)!=total:raise RuntimeError("Corrupt token count")
    return p[0],dec,[dec[st:en] for st,en in spans]

def replace_v4_popup_version(raw,L):
    result=bytearray()
    i=0
    changed=0
    while i<len(raw):
        op=raw[i]
        if 0x30<=op<=0x3f:
            n=struct.unpack_from("<I",raw,i+1)[0]
            sz=5+2*n
            if op==0x36:
                units=[struct.unpack_from("<H",raw,i+5+j*2)[0]^n for j in range(n)]
                old=struct.pack("<"+"H"*n,*units).decode("utf-16le")
                new=old.replace("26v4","26v5")
                if new!=old:
                    result+=L.st(op,new)
                    changed+=1
                else:result+=raw[i:i+sz]
            else:result+=raw[i:i+sz]
            i+=sz
        else:
            if op in (0x05,):step=5
            elif op in (0x10,0x20):step=9
            elif op<=0x0f:step=5
            elif op<=0x2f:step=9
            else:step=1
            result+=raw[i:i+step];i+=step
    if changed!=1:raise RuntimeError(f"Wrong popup version replacement count: {changed}")
    if len(result)!=len(raw):raise RuntimeError("Popup size unexpectedly changed")
    return bytes(result)

def append_guard_section(src,scriptres):
    L=lib()
    entries,d,_=L.resource_entries(src)
    last=max(d['secs'],key=lambda s:s['raw']+s['rs'])
    end=last['raw']+last['rs']
    if d['cert_off'] and d['cert_off']<end:raise RuntimeError("Overlapping certificate")
    if d['st']+(d['nsec']+1)*40>struct.unpack_from("<I",src,d['opt']+60)[0]:
        raise RuntimeError("No room for one PE section header")
    if len(scriptres)>12*1024*1024:raise RuntimeError("Unexpectedly large SCRIPT")
    blob=scriptres+b"\0"*((-len(scriptres))%FILE_ALIGN_MARKER)+MARKER
    rsize=L.align(len(blob),d['fa'])
    offset=L.align(end,d['fa'])
    image_va=L.align(max(s['va']+max(s['vs'],s['rs']) for s in d['secs']),d['sa'])
    raw=bytearray(src[:end])
    if offset>len(raw):raw.extend(b"\0"*(offset-len(raw)))
    raw+=blob
    raw+=b"\0"*(rsize-len(blob))
    # Update only SCRIPT RCDATA pointer and append a read-only .sguard section.
    descriptor,orig_rva,orig_size=entries[(10,"SCRIPT",0)]
    struct.pack_into("<II",raw,descriptor,image_va,len(scriptres))
    header=d['st']+d['nsec']*40
    raw[header:header+8]=b".sguard\0"
    struct.pack_into("<IIIIIIHHI",raw,header+8,len(blob),image_va,rsize,offset,0,0,0,0,0x40000040)
    struct.pack_into("<H",raw,d['coff']+2,d['nsec']+1)
    struct.pack_into("<I",raw,d['opt']+56,L.align(image_va+max(len(blob),rsize),d['sa']))
    struct.pack_into("<I",raw,d['opt']+8,struct.unpack_from("<I",src,d['opt']+8)[0]+rsize)
    overlay_start=len(raw)
    raw+=src[end:]
    if d['cert_off']:
        diff=d['cert_off']-end
        struct.pack_into("<II",raw,d['secdir'],overlay_start+diff,d['cert_sz'])
    ch=d['opt']+64
    struct.pack_into("<I",raw,ch,0)
    struct.pack_into("<I",raw,ch,L.pe_checksum(bytes(raw),ch))
    if raw.count(MARKER)!=1:raise RuntimeError("Guard marker not unique in EXE")
    return bytes(raw)

def build():
    import pefile
    if digest(BASE)!=V5_SHA:raise RuntimeError("Wrong 26v5 canonical base EXE")
    if digest(V4)!=V4_SHA:raise RuntimeError("Wrong 26v4 popup source EXE")
    L=lib()
    resource,orig,lines=script_code(BASE,L)
    _rv4,c4,lines4=script_code(V4,L)
    _rfrag,cfrag,compiled=script_code(FRAG,L)
    if len(lines)!=24069 or len(lines4)!=24027:
        raise RuntimeError(f"Unexpected legacy line count: v5={len(lines)}, v4={len(lines4)}")
    if not L.decode_line(lines[68]).startswith("( \"__SONG_FINAL_CLEANUP\""):
        raise RuntimeError("v5 startup insertion anchor missing")
    if not L.decode_line(lines4[69]).startswith("( 64 ,"):
        raise RuntimeError("26v4 creator popup not found")
    if not L.decode_line(lines4[70]).startswith("( 48 ,"):
        raise RuntimeError("26v4 security popup not found")
    # Compiled AutoIt guard module must begin with directives/functions and
    # end in exactly one top-level call to its native entrypoint.
    printed=[L.decode_line(x) for x in compiled]
    if not printed[-1].upper().startswith("__SONG_ISO_VERIFYOREXIT"):
        raise RuntimeError("Native compiled fragment entry missing")
    top=printed[0]
    if top!="#NoTrayIcon":raise RuntimeError("Fragment header mismatch: "+top)
    functions=compiled[1:-1]
    if not L.decode_line(functions[0]).upper().startswith("FUNC __SONG_ISO_STOP"):
        raise RuntimeError("Native fragment function layout mismatch")
    if not L.decode_line(functions[-1]).upper().startswith("ENDFUNC"):
        raise RuntimeError("Native fragment function ending missing")
    call=compiled[-1]
    a=replace_v4_popup_version(lines4[69],L)
    b=replace_v4_popup_version(lines4[70],L)
    # Runtime order: ISO full verification, original 26v4 popups, native GUI.
    result=lines[:69]+[call,a,b]+lines[69:]+functions
    if result[72:72+len(lines)-69]!=lines[69:]:
        raise RuntimeError("Original 26v5 tail altered")
    newcode=struct.pack("<I",len(result))+b"".join(result)
    newres=L.build_script_resource(resource,newcode)
    updated=append_guard_section(BASE.read_bytes(),newres)
    # Static decode must reproduce full expected token stream.
    _res,roundtrip,got=script_code_from_bytes(updated,L)
    if roundtrip!=newcode:raise RuntimeError("Final EA06 token roundtrip mismatch")
    baseline_res,_,_=parse_pe(BASE)
    new_res,_,_=parse_pe_bytes(updated)
    oldother={(tuple(x[0])):x[-1] for x in baseline_res if x[0][0]==10 and x[0][1]!="SCRIPT"}
    newother={(tuple(x[0])):x[-1] for x in new_res if x[0][0]==10 and x[0][1]!="SCRIPT"}
    if oldother!=newother:raise RuntimeError("Vendor RCDATA unexpectedly altered")
    if updated.count(MARKER)!=1:raise RuntimeError("Missing guard marker")
    p=pefile.PE(data=updated,fast_load=False);p.close()
    OUT.write_bytes(updated)
    STAGE.parent.mkdir(parents=True,exist_ok=True)
    if not (STAGE.parent/"Drivers").is_dir():raise RuntimeError("ISO_STAGE Drivers not fully copied")
    STAGE.write_bytes(updated)
    manifest={
       "name":"EDv9 26v5 Korean CLEAN + exact 26v4 popups + full RAW ISO seal",
       "stage":"UNSEALED_NOT_FOR_RELEASE",
       "base_sha256":V5_SHA,"original_popup_sha256":V4_SHA,
       "generated_exe_sha256":hashlib.sha256(updated).hexdigest().upper(),
       "new_token_lines":len(result),"original_token_lines_preserved":len(lines),
       "two_popup_rows_copied_from_26v4":True,
       "popup_titles_updated_to_26v5":True,
       "seal_expected_content":MARKER.decode(),
       "raw_iso_sha256_ready":False,
       "iso_e2e_tested":False}
    (ROOT/"edv9_guard_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

def parse_pe_bytes(data):
    # parse_pe operates on path. Temporary file only for strict resource checks.
    tmp=ROOT/"edv9_guard_static_tmp.exe"
    if tmp.exists():raise RuntimeError("Temporary static file exists")
    try:
        tmp.write_bytes(data)
        return parse_pe(tmp)
    finally:
        tmp.unlink(missing_ok=True)

def script_code_from_bytes(data,L):
    res,_,_=parse_pe_bytes(data)
    matches=[x[-1] for x in res if x[0][0]==10 and x[0][1]=="SCRIPT"]
    if len(matches)!=1:raise RuntimeError("Patched SCRIPT resource missing")
    meta,decoded,compression,expected=find_script_payload(matches[0],verbose=False)
    if compression:decoded=decompress_ea06(decoded)
    if len(decoded)!=expected:raise RuntimeError("Wrong decoded bytes")
    n,spans=L.line_slices(decoded)
    return matches[0],decoded,[decoded[a:b] for a,b in spans]

def find_unique_marker(iso):
    with iso.open("r+b") as f,mmap.mmap(f.fileno(),0) as mm:
        start=mm.find(PREFIX)
        if start<0:raise RuntimeError("Raw ISO seal marker absent")
        if mm.find(PREFIX,start+1)>=0:raise RuntimeError("Raw ISO contains multiple markers")
        read=bytes(mm[start:start+len(MARKER)])
        if not read.startswith(PREFIX) or not read.endswith(b"|END"):
            raise RuntimeError("Unexpected raw seal marker contents")
        return start

def patch_in_file(file_path,position,bytes_expected,replacement):
    if len(bytes_expected)!=len(replacement):raise RuntimeError("Patch length mismatch")
    with file_path.open("r+b") as f:
        f.seek(position)
        got=f.read(len(bytes_expected))
        if got!=bytes_expected:raise RuntimeError(f"Mismatch before patch {file_path}: {got!r}")
        f.seek(position);f.write(replacement);f.flush();os.fsync(f.fileno())

def patch_header(iso,iso_offset,total):
    offset_hex=("%016X"%iso_offset).encode()
    size_hex=("%016X"%total).encode()
    for path,marker_pos in [(iso,iso_offset),(STAGE,None),(OUT,None)]:
        if marker_pos is None:
            with path.open("rb") as f: data=f.read()
            marker_pos=data.find(PREFIX)
            if marker_pos<0 or data.find(PREFIX,marker_pos+1)>=0:
                raise RuntimeError(f"Incorrect marker in {path}")
        patch_in_file(path,marker_pos+OFF_BEGIN,b"0"*16,offset_hex)
        patch_in_file(path,marker_pos+SIZE_BEGIN,b"0"*16,size_hex)

def seal(iso):
    if not STAGE.is_file():raise RuntimeError("Missing staged new EXE")
    if not iso.is_file():raise RuntimeError("Missing oscdimg output ISO")
    iso_pos=find_unique_marker(iso)
    iso_size=iso.stat().st_size
    if iso_size<1_000_000_000:raise RuntimeError("Too-small ISO")
    patch_header(iso,iso_pos,iso_size)
    # Once O and S are patched, the SHA slot remains zero, so ordinary raw
    # ISO SHA256 equals normalized media SHA256.
    normalized=digest(iso)
    digest_field=normalized.encode("ascii")
    if len(digest_field)!=64:raise RuntimeError("Incorrect SHA length")
    for p,marker_pos in [(iso,iso_pos),(STAGE,None),(OUT,None)]:
        if marker_pos is None:
            with p.open("rb") as f:data=f.read()
            marker_pos=data.find(PREFIX)
            if marker_pos<0:raise RuntimeError(f"Not found {p}")
        patch_in_file(p,marker_pos+HASH_BEGIN,b"0"*64,digest_field)
    manifest=json.loads((ROOT/"edv9_guard_manifest.json").read_text("utf-8"))
    manifest.update({
        "stage":"SEALED_STATIC_PENDING_VM",
        "normalized_iso_sha256":normalized,
        "raw_iso_sha256":digest(iso),
        "iso_size":iso_size,
        "iso_digest_offset":iso_pos+HASH_BEGIN,
        "sealed_exe_sha256":digest(STAGE),
        "iso_e2e_tested":False,
    })
    (ROOT/"edv9_guard_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

def verify(iso):
    if not iso.is_file():raise RuntimeError("Missing ISO")
    with iso.open("rb") as f:
        m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
        at=m.find(PREFIX)
        if at<0 or m.find(PREFIX,at+1)>=0:raise RuntimeError("Seal marker not unique")
        marker=bytes(m[at:at+len(MARKER)])
        m.close()
    import re
    match=re.fullmatch(rb"EDV9_ISO_SEAL_V1\|O=([0-9A-F]{16})\|S=([0-9A-F]{16})\|H=([0-9A-F]{64})\|END",marker)
    if not match:raise RuntimeError("Malformed sealed marker")
    offset=int(match.group(1),16);expected_size=int(match.group(2),16);expected_sha=match.group(3).decode()
    if offset!=at or expected_size!=iso.stat().st_size:raise RuntimeError("ISO size / slot offset changed")
    hs=hashlib.sha256()
    start=at+HASH_BEGIN;end=start+64;position=0
    with iso.open("rb",buffering=0) as fp:
        while True:
            data=fp.read(8*1024*1024)
            if not data:break
            n=len(data)
            if position<end and position+n>start:
                data=bytearray(data)
                lower=max(start,position)
                upper=min(end,position+n)
                data[lower-position:upper-position]=b"0"*(upper-lower)
            hs.update(data)
            position+=n
    if hs.hexdigest().upper()!=expected_sha:raise RuntimeError("Raw ISO digest mismatch")
    source=STAGE.read_bytes()
    local=source.find(PREFIX)
    if local<0:raise RuntimeError("Local EXE seal missing")
    if bytes(source[local:local+len(marker)])!=marker:raise RuntimeError("Local EXE seal differs from ISO")
    print("FULL_RAW_ISO_NORMALIZED_SHA256=PASS",expected_sha)
    print("ISO_BYTES",position)
    print("SEALED_EXE_SHA256",digest(STAGE))
    return True

if __name__=="__main__":
    if len(sys.argv)<2:raise SystemExit("Usage: build | seal ISO | verify ISO")
    op=sys.argv[1].lower()
    if op=="build":build()
    elif op=="seal" and len(sys.argv)==3:seal(Path(sys.argv[2]))
    elif op=="verify" and len(sys.argv)==3:verify(Path(sys.argv[2]))
    else:raise SystemExit("Unknown command")
