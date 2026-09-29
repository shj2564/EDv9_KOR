# EDv9 26v5 Static Analysis — 2026-09-29

## Input

Archive:
`EDv9_26v5.zip`

Archive SHA-256:
`62A131570E3C33FEF76236C69D6B8DD24406CBE5FD6F62DAE187545A0C11BE43`

Core analysis ZIP contained:

| File | Size | SHA-256 |
|---|---:|---|
| EDv9_x64.exe | 14,598,168 | C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86 |
| EDv9_v9.0.2609.20009.dat | 256 | A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D |
| EDv9_x64.ini | 140 | 608E193A2B03A13C4F657F89A15B43CC40437906901DF8623B21FBA18775CCF2 |
| @version | 112 | 3C6923B48808D1B04B1280B447B7053F5CC8987EDCF1714B0FA1C83F422B633F |
| EDv9_26v5.shh | 67 | C68EEBC6AF5641989C4CCC9F8F19FC374086D64DD6A48B219F16B997A3ED4465 |

`EDv9_26v5.shh` text value:

`91768D1A811D140C66EDE9D3DAE9FCA33CEEBAF03F6ABF820E76A8739B1E9345`

## PE / AutoIt structure

`EDv9_x64.exe`:
- PE32+ / x86-64
- Windows GUI subsystem
- 6 PE sections
- AutoIt EA06 resource structure confirmed
- RCDATA `SCRIPT` resource file offset: `0xD8F428`
- Encrypted SCRIPT resource size: 360,996 bytes

AutoIt SCRIPT recovery:
- `>>>AUTOIT SCRIPT<<<` member found
- compressed payload: 360,528 bytes
- decompressed token stream: 2,582,467 bytes
- recovered source lines: 24,031
- token parse: 24,031 / 24,031 complete
- decompressed token SHA-256:
  `C915475435F6FDD5CCFE3281AF695F50C7A40ED6F9969E28DA9ABF4CB1776F79`

## XQS recovery

Decoded XQS:
- 4,940 string entries
- AutoIt-style array including count slot: 4,941 elements
- CJK-containing strings: 538
- Windows time/zone internal strings: 150
- other user-facing / operational CJK strings: 388

This is structurally very close to the previous 26v2/26v4 family and is suitable for differential Korean/CLEAN porting rather than a full rewrite.

## CLEAN-risk features present in 26v5

The decoded XQS contains all of the following:

| Target | XQS index / observation |
|---|---|
| SoftInst | 1415 |
| wget.exe | 375, 629, 3831, 4797 |
| inst.cmd | 2718 |
| inst.vbs | 3203 |
| https://123.itsk.com/d | 1442 |
| https://api.itsk.com/software_client | 2474 |
| https://www.2345.com/?751 | 573 |
| http://hao.360.com/?src=lm&ls=n3da59fa79e | 3184 |
| msedge.exe | 4455 |
| Edge PrefsLightweight | 3608 |
| startup_urls | 4806 |
| restore_on_startup | 303 |
| homepage | 3132 |
| UnmountDrv | 4852 |

### Code-path evidence

Recovered source references show active code paths, not only dead strings.

Edge-related function around recovered lines 2461–2504:
- references `msedge.exe`
- uses `homepage`
- uses `startup_urls`
- references Edge `PrefsLightweight`

Portal selection/cache function around lines 8499–8508:
- maps entries to 2345 and 360 URLs

SoftInst builder around lines 15045+:
- default target `SoftInst`
- builds/extracts `wget.exe`
- creates `inst.cmd`
- creates `inst.vbs`

ITSK API / download infrastructure:
- `https://api.itsk.com/software_client`
- `https://123.itsk.com/d`

UnmountDrv path:
- `UnmountDrv` is referenced around line 9054 and remains a separate normal cleanup/reboot path.
- It must be preserved during CLEAN patching.

## Initial conclusion

26v5 is **not CLEAN by default**. The same classes of online/after-install behavior previously identified in 26v2/26v4 remain present:
- SoftInst staging
- wget delivery helper
- inst.cmd / inst.vbs
- ITSK software API/download endpoint
- 2345 / 360 portal handling
- Edge process/settings manipulation

No conclusion is made here that EDv9 is a generic credential-stealing backdoor. This finding is narrower: these online/after-install mechanisms are unnecessary for the project's offline-driver-only objective and remain CLEAN-removal targets.

## Next work

1. Diff 26v5 token stream/XQS against 26v4 CLEAN baseline
2. Map prior 26v4 Korean translations into 26v5
3. Neutralize/remove the above online/post-install code paths
4. Keep UnmountDrv and driver install/mount paths intact
5. Validate DAT binding for modified 26v5 EXE
6. Build No-Residue one-click patcher
7. Static verification
8. Windows runtime verification
