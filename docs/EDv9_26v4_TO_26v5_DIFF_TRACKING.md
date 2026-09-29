# EDv9 26v4 → 26v5 Change Tracking

Date: 2026-09-29 KST

## Scope

This report compares the recovered AutoIt/XQS structure of the original EDv9 26v4 (`9.0.2608.20008`) with the original EDv9 26v5 (`9.0.2609.20009`), and projects the already verified 26v4 Korean CLEAN transformations onto 26v5.

The goal is not to re-localize from scratch. It is to prove which prior localization/CLEAN transformations can be transferred deterministically and identify any new 26v5-only work.

## Baselines

### 26v4 original
- EXE SHA-256: `FD2D3098A42B0922D4E17D159C16D313DC01EDDFDA67EF3AA5B11FD58852CDF2`
- recovered source lines: 24,014
- token bytes: 2,424,006
- token SHA-256: `F82AAEFFEB3D41F92745CD8C7EFB5E8EF0E4B40BEBD3455094BE103EFD1C3BD2`
- XQS entries: 4,940

### 26v4 CLEAN baseline
- base CLEAN EXE SHA-256: `6D0F312376C6389E6F118E69F46F2581FE8F898BD9A9D897AEF5178C3705C85D`
- correctly re-decoded CLEAN token bytes: 2,398,103
- CLEAN token SHA-256: `5B3ECE0789456418898EB692A8B67255F4E7F98B9E61567017E896316C723B8B`
- XQS changes vs original: 419
  - Korean/localization targets: 388
  - CLEAN/non-Hangul targets: 31

### 26v5 original
- ZIP SHA-256: `62A131570E3C33FEF76236C69D6B8DD24406CBE5FD6F62DAE187545A0C11BE43`
- EXE SHA-256: `C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86`
- DAT SHA-256: `A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D`
- recovered source lines: 24,031
- token bytes: 2,582,467
- token SHA-256: `C915475435F6FDD5CCFE3281AF695F50C7A40ED6F9969E28DA9ABF4CB1776F79`
- XQS entries: 4,940

## Result 1 — Korean UI set is unchanged

Raw 26v4 and raw 26v5 each contain:
- 4,940 XQS entries
- 538 CJK-containing strings

Set comparison of the CJK strings:
- present in 26v4 but absent in 26v5: **0**
- new in 26v5 compared with 26v4: **0**

Therefore no new Chinese UI/message string requiring translation was identified in 26v5.

The previous 388 Korean translation targets cover the same CJK source strings.

## Result 2 — 419/419 prior XQS transformations map exactly

The 26v4 CLEAN baseline changes 419 XQS entries.

For each changed 26v4 source value, the original value was searched in raw 26v5:
- uniquely mapped: **419**
- unmapped: **0**
- ambiguous: **0**

Breakdown:
- localization/Hangul targets: **388/388**
- CLEAN/non-Hangul targets: **31/31**

This means the complete previous XQS patch can be transferred to 26v5 deterministically by source-value identity, despite XQS index shuffling between releases.

`patches/26v5/port_manifest.json` records the resolved v5 target index, SHA-256 of the expected source value, and replacement target for all 419 transformations.

## Result 3 — Raw XQS changes from 26v4 to 26v5 are small and non-UI

Across raw XQS value sets:
- common unique values: 4,843
- v4-only values: 38
- v5-only values: 38

The 38 replaced values are build/obfuscation metadata rather than new Chinese user-facing UI:
- obfuscated identifiers
- generated/dynamic expression strings
- encoded blob values
- release marker `26v4` → `26v5`

No new CJK value was introduced.

## Result 4 — function layout was shuffled, but every CLEAN target was recovered

Both builds contain 1,069 functions.

Semantic normalization produced:
- 962 uniquely exact function mappings immediately
- 24 ambiguous signature groups covering 59 additional functions
- remaining unrelated functions can be resolved later by graph/context when necessary

Critically, **all 10 code locations used by the 26v4 CLEAN core were mapped exactly to 26v5**:

| 26v4 function | 26v5 function | v5 lines | mode |
|---|---|---:|---|
| ABUTKYYLVUQT | ZTQHGTQOWQRP | 512–523 | NOOP_SUCCESS |
| FVHBZAFSEZWV | HWFIGTLUCJGT | 2461–2504 | NOOP_SUCCESS |
| PMUMLROKASPU | LILDMLEEWQXW | 8591–8623 | ERROR_RETURN |
| KFVZVYQVUXYK | RZRYBIBECJJX | 3643–3702 | NOOP_SUCCESS |
| ZNSTVPCNEVVF | JSDJXQCWGIEC | 10401–10409 | NOOP_SUCCESS |
| AGOUKQLTKNTD | WPABAGMJSZMP | 9993–10081 | ERROR_RETURN |
| YQSXEOHCIHKW | HGESOPLHTLUD | 18084–18108 | NOOP_SUCCESS |
| ARTPTMMQTIJM | NBNYSWNQRHCU | 23348–23353 | NOOP_SUCCESS |
| SXHYUKMWTDOY | RKLCKDUPGHET | 15045–15108 | NOOP_SUCCESS |
| VXXEGIHNEIZN | VJFAVTHSAIJL | 8800–8826 | BLANK_BIND_RETURN |

For `VJFAVTHSAIJL`, only recovered line **8823** is to be blanked. DAT structure/version/architecture validation remains intact.

## Result 5 — known unwanted mechanisms remain structurally equivalent

26v5 still contains active references for:
- Edge process/profile/startup/homepage handling
- SoftInst staging
- wget helper
- `inst.cmd` / `inst.vbs`
- ITSK software API and 123 download endpoint
- 2345 / 360 portal mappings

Their obfuscated function names/indices changed, but the prior CLEAN strategy is still applicable.

`UnmountDrv` remains separately present and is not part of the removal set.

## Dispatcher/index mapping

From aligned functions:
- 1,149 dispatcher indices mapped
- no ambiguous mappings
- target indices are unique

Context + exact-value XQS mapping covers **4,933 / 4,940** indices without conflict.

The 7 unresolved XQS entries are obfuscation/generated metadata and are not among the 419 Korean/CLEAN transformations.

## 26v5 return templates

Mapped equivalent of the 26v4 CLEAN success return:

```autoit
RETURN $SAHBLBIS [ 976 ] ( $QZQMHBTU [ 4249 ] , $QZQMHBTU [ 4249 ] , $QZQMHBTU [ 4249 ] )
```

Mapped equivalent of the error return:

```autoit
RETURN $SAHBLBIS [ 976 ] ( $QZQMHBTU [ 4615 ] , $QZQMHBTU [ 4249 ] , $QZQMHBTU [ 4249 ] )
```

## Decision

**26v5 does not require a new Korean translation pass.**

The correct path is:
1. apply the 419-entry XQS port manifest,
2. apply the 10 mapped code neutralizations,
3. re-encode/repack the EA06 resources,
4. verify forbidden strings are absent,
5. verify `UnmountDrv` and core driver paths remain,
6. verify DAT behavior,
7. build the No-Residue patcher,
8. perform Windows runtime testing.

## Current status

Change tracking: **COMPLETE for the Korean/CLEAN transfer surface.**

Next stage: **construct the 26v5 patched resources and executable, then static-verify them before any Windows runtime test.**