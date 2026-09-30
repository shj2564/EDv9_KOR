# EDv9 26v5 FINAL ISO Build

Prepared: 2026-09-30 KST

## Builder

File:
`EDv9_26v5_FINAL_Make_ISO_OneClick.cmd`

Builder SHA-256:
`D1823828CE8307251F5DB7DEF3C9B7A01083B3E3693FDF42A952AEBE21B477DE`

## Input baseline

- FINAL EXE: `EDv9_x64_KO_CLEAN.exe`
- FINAL EXE SHA-256: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`
- DAT SHA-256: `A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D`
- INI SHA-256: `608E193A2B03A13C4F657F89A15B43CC40437906901DF8623B21FBA18775CCF2`
- Drivers/@version SHA-256: `3C6923B48808D1B04B1280B447B7053F5CC8987EDCF1714B0FA1C83F422B633F`
- Original EXE SHA-256 (verified if present, excluded from ISO): `C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86`
- OSCDIMG verified SHA-256: `801D8BC3FFA4C15B1740C3FAE78612243315F35ED0683E28C22570A6F5A251A9`

## ISO policy

Output:
`EDv9_26v5_KO_CLEAN_FINAL.iso`

- UDF 1.02
- volume label: `EDv9_26v5_KO`
- ISO root contains only:
  - `EDv9_x64_KO_CLEAN.exe`
  - `EDv9_x64.ini`
  - `EDv9_v9.0.2609.20009.dat`
  - `Drivers/`
- original `EDv9_x64.exe` is excluded
- recursive EXE count must be exactly 1
- source folder is not modified
- ISO-only staging uses hardlinks where possible, falling back to copy
- staging is removed after build
- created ISO is mounted and revalidated
- file count and payload byte total must match
- FINAL EXE hash inside mounted ISO must match
- ISO SHA-256 is calculated after validation and written to:
  - `EDv9_26v5_KO_CLEAN_FINAL.sha256.txt`
  - `EDv9_26v5_KO_CLEAN_FINAL.ISO_BUILD_REPORT.txt`
- ISO SHA-256 is copied to Windows clipboard at completion

## Status

Builder prepared. Final ISO SHA-256 is generated on the Windows machine holding the complete 26v5 Drivers set and should be recorded here after the build completes.
