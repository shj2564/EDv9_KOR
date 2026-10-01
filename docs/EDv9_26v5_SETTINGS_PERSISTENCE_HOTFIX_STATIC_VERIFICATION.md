# EDv9 26v5 Settings Persistence HOTFIX — Static Verification

Date: 2026-10-01 KST

## Background

Runtime feedback showed that changing **Driver package mode** / **Driver install after** in Settings and clicking **Apply settings** did not survive a process restart. Direct analysis of the original 26v5 AutoIt EA06 script confirmed that the vendor build applies these values only to current-process variables; it does not persist them.

The existing Korean label `설정 적용` is therefore semantically correct for the original behavior. This HOTFIX adds persistence as a new Korean CLEAN feature.

## Input baseline

Canonical runtime-verified FINAL baseline:

- EXE: `EDv9_x64_KO_CLEAN.exe`
- SHA-256: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`
- Size: 20,427,288 bytes
- Token SHA-256: `C2FE0C9D5FBA4A43697A81798710C0A164E5EB1BEB62E66B494EBCB15A9F6861`
- Token lines: 24,042

## Candidate

- Candidate SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`
- Candidate size: 22,985,240 bytes
- Candidate token SHA-256: `8FB9D574B1D29A18DA56D344DEF63EDF51E106765579169579528D46CF164624`
- Token lines: 24,069
- Added PE section: `.kpref`

## Persistence design

Storage:

`HKCU\Software\SoNG\EDv9_KOR`

Values:

- `Extract` — REG_DWORD
- `NeedReboot` — REG_DWORD

Only behavior preferences are persisted.

The target Windows folder is deliberately **not** persisted because it is environment-specific and may differ between normal Windows, WinPE, offline servicing, or a different machine. EDv9 continues to auto-detect it on every run.

## Precedence / compatibility

The original command-line semantics are preserved.

- Forced `/Extract` keeps priority over a saved Extract preference.
- Forced no-reboot conditions (`/NoReboot`, `/nr`, and the original deploy-mode-derived no-reboot state) keep priority over a saved NeedReboot preference.
- Missing registry values fall back to the original EDv9 defaults.
- Invalid/missing saved state does not block launch.

An exhaustive 36-case state-model test covering saved missing/0/1 × force states passed.

## Exact insertion points

1. Preference LOAD call is inserted immediately after original 26v5 initializes the runtime `Extract` and `NeedReboot` variables.
2. Preference SAVE call is inserted only inside the existing successful Settings-Apply branch, after the original settings parser returns without `@ERROR`.

The original Settings apply function is otherwise untouched.

## Function map guards

The active original function map was reconstructed from the recovered script and checked:

- `SAHBLBIS[164] = REGREAD` — PASS
- `SAHBLBIS[176] = INT` — PASS
- `SAHBLBIS[1120] = REGWRITE` — PASS

No new direct AutoIt built-in opcode was introduced; the HOTFIX follows the existing obfuscated function-dispatch mechanism.

## Token integrity

- Original 24,042 FINAL token lines preserved byte-for-byte: PASS
- Added call lines: 2
- Added helper lines: 25
- Generated macro spelling: canonical `@ERROR` only — PASS
- Regular Func/EndFunc after patch: 1071/1071, plus the existing proven cleanup Func — PASS
- Active SCRIPT decrypt/reparse: PASS
- Existing C:\Drivers cleanup token block: byte-identical PASS

## PE preservation

Byte-identical to the canonical FINAL:

- `.text`
- `.rdata`
- `.data`
- `.pdata`
- `.reloc`
- `.kscr`
- `.kres`
- `.kcln`

Other checks:

- non-SCRIPT resources: RVA / size / data exact PASS
- `.rsrc`: only SCRIPT resource redirect fields changed (4 differing bytes)
- Authenticode certificate blob bytes: exact PASS
- PE checksum: PASS
- PE remains PE32+ x86-64 Windows GUI
- Vendor signature validity remains invalid, as with all modified builds

## CLEAN preservation

The HOTFIX introduces no SoftInst / wget / inst.cmd / inst.vbs / ITSK / 2345 / 360 / Edge targets.

Driver scan, matching, DB/WIM handling, driver installation, DAT handling, UnmountDrv, and the existing safe C:\Drivers cleanup logic are not modified.

## Status

**STATIC VERIFIED TEST CANDIDATE**

The canonical FINAL hash remains:

`955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`

until Windows runtime persistence + normal driver-flow smoke tests pass.

Required runtime gate:

1. Settings → change package mode / restart behavior → Apply.
2. Exit and relaunch.
3. Confirm saved options restore.
4. Confirm `/NoReboot` or `/nr` still overrides saved restart preference.
5. Confirm normal scan / driver list / actual install / completion button remain normal.
