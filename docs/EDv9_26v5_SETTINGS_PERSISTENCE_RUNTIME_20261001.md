# EDv9 26v5 Settings Persistence HOTFIX — Windows Runtime Result

Date: 2026-10-01 KST

## Tested candidate

- EXE: `EDv9_x64_KO_CLEAN.exe`
- SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`
- Base FINAL: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`

## Persistence runtime tests

User-confirmed Windows tests:

1. **Driver install after**
   - Settings → `수동 재시작 대기` → `설정 적용` → exit → relaunch
   - `수동 재시작 대기` remained selected after relaunch
   - Result: **PASS**

2. **Driver package mode**
   - Changed the package-mode setting, applied it, exited, relaunched
   - Selected mode remained stored
   - Result: **PASS**

3. **Scan / driver list**
   - Hardware scan: **PASS**
   - Driver list UI/path: **PASS**
   - On the tested machine, no installable entries were shown because its drivers were already installed.

## Regression assessment for untouched paths

The persistence HOTFIX changes only:
- one preference-load call after `Extract` / `NeedReboot` initialization
- one preference-save call after successful Settings Apply
- appended persistence helper functions

The original FINAL token stream is otherwise preserved byte-for-byte.

Therefore these previously runtime-verified paths remain implementation-identical to the prior FINAL:
- actual driver installation
- completion button
- UnmountDrv handling
- safe `C:\Drivers` cleanup
- CLEAN OFFLINE neutralization

They were **not re-executed on this exact candidate in the 2026-10-01 session**, so they are recorded as **inherited by exact-code preservation**, not as a new candidate-specific runtime PASS.

## Release assessment

Changed/touched paths:
- launch: PASS
- Settings UI: PASS
- Settings Apply: PASS
- `Extract` persistence: PASS
- `NeedReboot` persistence: PASS
- relaunch/restore: PASS
- scan: PASS
- driver-list path: PASS

Untouched critical paths:
- exact-code preservation from previously multi-PC runtime-verified FINAL: PASS

## Status

**PROMOTION-READY — SETTINGS PERSISTENCE RUNTIME VERIFIED**

This candidate is eligible to replace the previous FINAL EXE baseline.

Important release hygiene:
- The existing full ISO hash `F660C0A32E98ECCDDBEABF744B9FB380807F8C42F34551773A19DCD1F33D8261` belongs to the previous FINAL EXE and must not be advertised as containing this new settings-persistence EXE.
- A new ISO must be rebuilt before publishing a new canonical ISO hash.
