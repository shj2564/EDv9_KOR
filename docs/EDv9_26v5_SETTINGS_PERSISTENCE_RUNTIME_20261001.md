# EDv9 26v5 Settings Persistence HOTFIX — Windows Runtime Result

Date: 2026-10-01 KST

## Tested candidate

- EXE: `EDv9_x64_KO_CLEAN.exe`
- SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`
- Base FINAL: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`

## Persistence runtime test

User-confirmed Windows test sequence:

1. Open Settings.
2. Change **Driver install after** to **수동 재시작 대기**.
3. Click **설정 적용**.
4. Exit EDv9.
5. Relaunch EDv9.
6. Re-open Settings.

Observed result:

- **수동 재시작 대기 remained selected after relaunch: PASS**

This confirms the new `NeedReboot` persistence load/save path is functioning at runtime.

## Current gate status

PASS:
- Program launch
- Settings UI opens
- Settings Apply path executes
- `NeedReboot` saved
- `NeedReboot` restored after process restart

Still recommended before FINAL promotion:
- Persist/reload the package mode (`Extract`) once
- Confirm `/NoReboot` or `/nr` override remains effective
- Scan / driver list smoke test
- Actual driver install
- Completion button
- Existing C:\Drivers cleanup regression check

## Status

**SETTINGS PERSISTENCE RUNTIME PASS / FULL REGRESSION GATE PENDING**

The previous multi-PC runtime-verified FINAL remains canonical until the full regression gate is complete.
