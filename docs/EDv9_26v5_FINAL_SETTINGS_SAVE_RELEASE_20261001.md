# EDv9 26v5 Korean CLEAN SettingsSave FINAL — Release Snapshot

Date: 2026-10-01 KST

## Canonical release

Version:
- EDv9 26v5
- Internal version: 9.0.2609.20009
- Edition: Korean CLEAN OFFLINE No-Residue + Settings Persistence

FINAL EXE:
- File: `EDv9_x64_KO_CLEAN.exe`
- SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`
- Size: 22,985,240 bytes
- Token SHA-256: `8FB9D574B1D29A18DA56D344DEF63EDF51E106765579169579528D46CF164624`

FINAL ISO:
- File: `EDv9_26v5_KO_CLEAN_FINAL.iso`
- SHA-256: `6AD8DC770FDDB2E27782131B6A2AB4F48C66BB66416C51AE8856EE549C96B536`
- Size: 11,951,794,176 bytes
- Filesystem: UDF 1.02
- Volume label: `EDv9_26v5_KO`
- Payload file count: 106
- Payload bytes: 11,950,815,374
- Build time: 2026-10-01 19:02:16 KST
- Validation: PASS

## Runtime verification

Confirmed on Windows:
- Program launch: PASS
- Korean UI: PASS
- Hardware scan: PASS
- Driver-list path: PASS
- Driver package-mode persistence: PASS
- Driver install-after persistence: PASS
- Settings survive exit/relaunch: PASS

Previously verified and byte-identical preserved paths:
- Actual driver installation
- Completion button
- UnmountDrv
- C:\Drivers safe cleanup
- CLEAN OFFLINE neutralization
- SoftInst / unwanted RunOnce absence

## Settings persistence

Storage:
`HKCU\Software\SoNG\EDv9_KOR`

Values:
- `Extract` (REG_DWORD)
- `NeedReboot` (REG_DWORD)

Current Korean UI wording:
- 대상 Windows 폴더
- 드라이버 패키지 사용 방식
  - `마운트 (압축 해제 없이 사용)`
  - `압축 해제 (특수 환경용)`
- 드라이버 설치 후
  - `모두 설치한 후 자동 재시작`
  - `수동 재시작 대기`
- `설정 적용`

Target Windows folder is intentionally not persisted and remains auto-detected each run.

## ISO root policy

The canonical ISO root contains only:
- `EDv9_x64_KO_CLEAN.exe`
- `EDv9_x64.ini`
- `EDv9_v9.0.2609.20009.dat`
- `Drivers\`

The original `EDv9_x64.exe` is excluded.

## Final documentation images

The user-guide artwork was regenerated on 2026-10-01 using the actual Settings screenshots and corrected wording. The final guide explicitly documents:
- Settings persistence behavior
- Current package-mode strings
- Current reboot-mode strings
- FINAL EXE SHA-256
- ISO mount/run/scan/install/completion workflow

## Status

**EDv9 26v5 Korean CLEAN OFFLINE No-Residue + Settings Persistence — FINAL ISO VERIFIED**
