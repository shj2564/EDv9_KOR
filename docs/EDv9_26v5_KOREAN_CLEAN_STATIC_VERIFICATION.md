# EDv9 26v5 Korean CLEAN OFFLINE — Static Verification

Date: 2026-09-29 KST

## Build identity

- Original EXE SHA-256: `C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86`
- Candidate EXE: `EDv9_x64_KO_CLEAN.exe`
- Candidate EXE SHA-256: `40D5155F455260AC750B65BA80499B8C88673C3DCA18EAA750C26D238A886D89`
- Candidate size: 17,870,872 bytes
- Original DAT SHA-256: `A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D`
- Original DAT is unchanged.
- TEST one-click patcher SHA-256: `65ED8BB484688E7F46E1D0AB07AB03DFDCC4276DE9D3D6AB8B9B9D728C21C21F`
- Verification report SHA-256: `C7822428DB380FAA707351299A280189E0CEE3D50A8803B95B3B3311401F87CB`

## Regression gate before 26v5 build

The 26v5 SCRIPT neutralization algorithm was first applied to the original 26v4 EA06 token stream.

Result: the generated 26v4 token stream was **byte-for-byte identical** to the known verified 26v4 Base CLEAN token stream.

- Known 26v4 Base CLEAN token SHA-256: `5B3ECE0789456418898EB692A8B67255F4E7F98B9E61567017E896316C723B8B`
- Regenerated token SHA-256: same
- Exact binary equality: PASS

This regression gate is important because the 26v5 code neutralization uses the same token-level method rather than newly invented source-level logic.

## XQS localization / CLEAN data

- Total constants: 4,940
- Verified 26v4 → 26v5 mappings applied: **419/419 PASS**
- Korean localization replacements: 388
- CLEAN/non-Hangul replacements: 31
- Remaining CJK: 150
- Remaining CJK classification: all 150 are `Time:...|Zone:...` timezone/internal comparison records
- Unexpected user-facing CJK: 0
- UnmountDrv retained: PASS, XQS index 4852
- Rebuild → decrypt exact target roundtrip: PASS

### CLEAN literal verification

Network/portal substrings are absent from the decoded XQS and direct binary scan:

- `123.itsk.com`: absent
- `api.itsk.com`: absent
- `www.2345.com`: absent
- `hao.360.com`: absent

Original operational exact XQS values are absent:

- `SoftInst`
- `wget.exe`
- `inst.cmd`
- `inst.vbs`
- `msedge.exe`
- `PrefsLightweight`
- `startup_urls`
- `restore_on_startup`
- `homepage`

Note: inert replacement markers intentionally use names such as `__clean_disabled_homepage` or `__clean_disabled_startup_urls`. Therefore the verification criterion is the absence of the **original operational exact values**, not an inaccurate claim that every word fragment is absent.

## AutoIt EA06 SCRIPT

- Patched token bytes: 2,554,876
- Patched token SHA-256: `625608E90CD49C9E45623882FDAD9C4271D72C60212CBE73BAA5F07FEC5FEA59`
- Source/token lines: 24,031
- Func / EndFunc: 1,069 / 1,069 PASS
- CLEAN neutralization targets: 10/10 PASS
- DAT validation: version/structure/architecture checks retained; hash-mismatch RETURN only blanked
- Macro vocabulary: subset of original 26v5 macro set, no newly introduced unknown macro
- Rebuilt SCRIPT resource decrypt/reparse: PASS

Mapped CLEAN functions:

| 26v4 verified target | 26v5 target | Action |
|---|---|---|
| ABUTKYYLVUQT | ZTQHGTQOWQRP | NOOP success |
| FVHBZAFSEZWV | HWFIGTLUCJGT | NOOP success |
| PMUMLROKASPU | LILDMLEEWQXW | error return |
| KFVZVYQVUXYK | RZRYBIBECJJX | NOOP success |
| ZNSTVPCNEVVF | JSDJXQCWGIEC | NOOP success |
| AGOUKQLTKNTD | WPABAGMJSZMP | error return |
| YQSXEOHCIHKW | HGESOPLHTLUD | NOOP success |
| ARTPTMMQTIJM | NBNYSWNQRHCU | NOOP success |
| SXHYUKMWTDOY | RKLCKDUPGHET | NOOP success |
| VXXEGIHNEIZN | VJFAVTHSAIJL | hash-mismatch RETURN only blanked |

## PE preservation

- `.text`: byte-identical PASS
- `.rdata`: byte-identical PASS
- `.data`: byte-identical PASS
- `.pdata`: byte-identical PASS
- `.reloc`: byte-identical PASS
- `.rsrc`: only resource RVA/size redirection fields changed; 26 differing bytes
- Added read-only initialized sections: `.kscr`, `.kres`
- Original Authenticode certificate blob bytes: byte-identical PASS
- PE checksum: PASS

Any executable modification invalidates the vendor's Authenticode signature validity even if the original certificate blob is preserved.

## TEST one-click patcher safeguards

The TEST patcher:

- requires the exact 26v5 original EXE/DAT/INI hashes before applying
- never overwrites `EDv9_x64.exe`
- creates only `EDv9_x64_KO_CLEAN.exe`
- preserves DAT / INI / Drivers
- refuses to overwrite a different existing CLEAN EXE
- verifies the embedded candidate SHA-256 before and after writing
- `/restore` deletes only the exact matching candidate it created
- removes its temporary `.tmp` / `.new` / dedicated TEMP residue
- does **not** automatically launch the candidate
- embedded payload decompresses to the candidate byte-for-byte: PASS

The Windows CMD/PowerShell wrapper has been statically inspected, but it has not been executed in the Linux analysis environment.

## Status

**STATIC VERIFIED / WINDOWS RUNTIME TEST REQUIRED**

The build must not be promoted to FINAL until the following real Windows path passes:

1. launch
2. Korean UI / DB load
3. hardware scan
4. driver list
5. settings
6. actual driver install
7. **completion button**
8. legitimate UnmountDrv/reboot cleanup
9. no SoftInst RunOnce/folder and no Edge configuration change

The completion-button step is mandatory because a previous optional 26v4 V1.0 post-build addition exposed an AutoIt token defect there; this 26v5 candidate deliberately ports the verified Base CLEAN logic without that appended V1.0 cleanup function.
