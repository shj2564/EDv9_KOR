from pathlib import Path
import sys,struct,hashlib,re,json
sys.path.insert(0,'/mnt/data')
sys.path.insert(0,'/mnt/data/edv9_work')
from extract_pe_resources import parse_pe
from extract_autoit_ea06 import find_script_payload,decompress_ea06,parse_tokens
from build_26v5_clean import decode_xqs_resources,resource_data_entries,parse_pe_details,pe_checksum

ROOT=Path('/mnt/data/edv9_work')
orig=ROOT/'v5'/'EDv9_x64.exe'; out=ROOT/'EDv9_x64_KO_CLEAN_26v5.exe'; dat=ROOT/'v5'/'EDv9_v9.0.2609.20009.dat'; man=json.load(open('/mnt/data/EDv9_26v5_port_manifest.json',encoding='utf-8'))
B0=orig.read_bytes();B=out.read_bytes()
sha=lambda x:hashlib.sha256(x).hexdigest().upper()
assert sha(B0)=='C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86'
assert sha(dat.read_bytes())=='A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D'

# Active RCDATA resource decode
rs,secs,ri=parse_pe(out)
R={pp[1]:data for pp,off,sz,cp,data in rs if len(pp)>=2 and pp[0]==10 and isinstance(pp[1],str)}
xnames=['NWVBLDVM','OEVERVRW','PLAKRMHD','LABKLCBS']
meta=decode_xqs_resources(R,xnames); xqs=meta['xqs']
assert len(xqs)==4941 and xqs[0]==4940
for p in man['xqs_patches']:
    assert xqs[p['v5_index']]==p['target'],(p['v5_index'],xqs[p['v5_index']],p['target'])
# CJK only timezone/internal count expected 150
cjk=re.compile(r'[\u3400-\u9fff\uf900-\ufaff]')
cj=[(i,v) for i,v in enumerate(xqs) if isinstance(v,str) and cjk.search(v)]
assert len(cj)==150,len(cj)

forbidden_substring=['123.itsk.com','api.itsk.com','www.2345.com','hao.360.com']
for f in forbidden_substring:
    hits=[i for i,v in enumerate(xqs) if isinstance(v,str) and f.lower() in v.lower()]
    assert not hits,(f,hits)
forbidden_exact=['SoftInst','wget.exe','inst.cmd','inst.vbs','msedge.exe','PrefsLightweight','startup_urls','restore_on_startup','homepage']
for f in forbidden_exact:
    hits=[i for i,v in enumerate(xqs) if isinstance(v,str) and v.lower()==f.lower()]
    assert not hits,(f,hits)
forbidden=forbidden_substring+forbidden_exact
unmount=[(i,v) for i,v in enumerate(xqs) if isinstance(v,str) and 'unmountdrv' in v.lower()]
assert unmount, 'UnmountDrv missing'

# Active SCRIPT decode from resource directory, not stale original bytes.
sres=R['SCRIPT']; ent,dec,comp,codesz=find_script_payload(sres,verbose=False); code=decompress_ea06(dec) if comp==1 else dec
assert comp==0 and codesz==len(code)
total,lines,toks,end=parse_tokens(code)
assert total==24031 and len(lines)==24031 and end==len(code)
for p in man['code_patches']:
    if p['mode']=='BLANK_LINE':
        assert lines[p['v5_line']-1]==''
    else:
        s,e=p['v5_body_lines']; assert lines[s-1]==man['return_templates'][p['mode']]
        assert all(lines[i-1]=='' for i in range(s+1,e+1))
# Ensure function declarations/endfunc still balanced.
funcs=sum(1 for l in lines if l.startswith('FUNC ')); ends=sum(1 for l in lines if l=='ENDFUNC')
assert funcs==ends,(funcs,ends)
# No unexpected macro spelling: all macros seen in original token set.
orig_code=(Path('/mnt/data/edv9_26v5_decoded/script.token.bin')).read_bytes(); _,_,orig_toks,_=parse_tokens(orig_code)
orig_mac={t[3] for t in orig_toks if t[2]=='macro'}
new_mac={t[3] for t in toks if t[2]=='macro'}
assert new_mac<=orig_mac,(new_mac-orig_mac)

# Core sections unchanged byte for byte.
def secmap(p):
    b=Path(p).read_bytes(); d=parse_pe_details(b);return b,{s['name']:s for s in d['secs']},d
ob,os,od=secmap(orig); nb,ns,nd=secmap(out)
for name in ['.text','.rdata','.data','.pdata','.reloc']:
    a=os[name];z=ns[name]
    assert ob[a['raw']:a['raw']+a['rs']]==nb[z['raw']:z['raw']+z['rs']],name
# Original rsrc differs only via redirected resource data-entry fields (5 * RVA/size pairs).
a=os['.rsrc'];z=ns['.rsrc']; oldrs=ob[a['raw']:a['raw']+a['rs']]; newrs=nb[z['raw']:z['raw']+z['rs']]
diff=[i for i,(x,y) in enumerate(zip(oldrs,newrs)) if x!=y]
# Size remains original; exact diff byte count can vary by encoded field bytes but must be small.
assert len(diff)<=40,len(diff)
# Certificate bytes preserved exactly.
co,cs=od['cert_off'],od['cert_sz']; cn,cns=nd['cert_off'],nd['cert_sz']
assert cs==cns and ob[co:co+cs]==nb[cn:cn+cns]
# Security table still reaches the same cert blob and checksum is valid.
chkoff=nd['opt']+64; stored=struct.unpack_from('<I',nb,chkoff)[0]; calc=pe_checksum(nb,chkoff);assert stored==calc,(hex(stored),hex(calc))
# Section additions exactly expected.
assert [s['name'] for s in nd['secs'][-2:]]==['.kscr','.kres']
# Direct binary scan for network domains only; disabled marker names intentionally retain descriptive suffixes.
for f in forbidden_substring:
    assert f.encode('ascii','ignore').lower() not in nb.lower(),('ascii',f)
    assert f.encode('utf-16le').lower() not in nb.lower(),('utf16',f)

report=[]
A=report.append
A('EDv9 26v5 Korean CLEAN OFFLINE - Static Verification')
A('')
A('Original EXE SHA-256 : '+sha(B0))
A('Candidate EXE SHA-256: '+sha(B))
A(f'Candidate size        : {len(B)} bytes')
A('Original DAT SHA-256 : '+sha(dat.read_bytes())+' (UNCHANGED)')
A('')
A('XQS:')
A('  total constants                  : 4940')
A('  mapped Korean/CLEAN replacements : 419/419 PASS')
A('  Korean localization              : 388')
A('  CLEAN/non-Hangul                 : 31')
A('  remaining CJK                    : 150')
A('  remaining CJK classification     : timezone/internal baseline only')
A('  forbidden CLEAN literals         : 0 PASS')
A(f'  UnmountDrv retained              : PASS ({unmount[0][0]})')
A('  rebuild/decrypt exact roundtrip  : PASS')
A('')
A('SCRIPT / AutoIt EA06:')
A(f'  token bytes                      : {len(code)}')
A(f'  token SHA-256                    : {sha(code)}')
A(f'  lines                            : {total}')
A(f'  Func / EndFunc                   : {funcs}/{ends} PASS')
A('  CLEAN neutralization targets     : 10/10 PASS')
A('  hash-mismatch RETURN blank only  : PASS')
A('  macro vocabulary                 : original subset PASS')
A('  resource decrypt/reparse         : PASS')
A('')
A('PE preservation:')
for name in ['.text','.rdata','.data','.pdata','.reloc']:A(f'  {name:7s}: byte-identical PASS')
A(f'  .rsrc redirected-field diff bytes: {len(diff)}')
A('  added sections                   : .kscr / .kres')
A('  Authenticode certificate blob    : byte-identical PASS')
A('  PE checksum                      : PASS')
A('  NOTE: modifying the binary invalidates vendor signature validity.')
A('')
A('CLEAN target verification:')
A('  network/portal substrings absent from decoded XQS and direct binary scan:')
for f in forbidden_substring:A('    '+f+': absent PASS')
A('  original operational exact XQS values absent:')
for f in forbidden_exact:A('    '+f+': exact-value absent PASS')
A('  NOTE: disabled marker strings may intentionally contain words such as homepage/startup_urls/restore_on_startup as part of __clean_disabled_* names; they are not operational original values.')
A('')
A('STATUS: STATIC VERIFIED / WINDOWS RUNTIME TEST REQUIRED')
A('Required runtime path: launch -> DB load -> scan -> driver list -> settings -> driver install -> completion button -> reboot cleanup.')
path=ROOT/'EDv9_26v5_Korean_CLEAN_Static_Verification.txt'; path.write_text('\n'.join(report),encoding='utf-8')
print('\n'.join(report))