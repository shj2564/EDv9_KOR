# EDv9 26v5 Korean CLEAN OFFLINE — Windows Runtime Verification

Date: 2026-09-30 KST

## Tested build

Executable:
`EDv9_x64_KO_CLEAN.exe`

SHA-256:
`40D5155F455260AC750B65BA80499B8C88673C3DCA18EAA750C26D238A886D89`

Original release:
- EDv9 26v5
- Internal version: 9.0.2609.20009

## Real Windows test result

User-confirmed real Windows execution:

- Program launch: **PASS**
- Korean UI rendering: **PASS**
- Hardware scan / detected device list: **PASS**
- Driver install workflow entered normally: **PASS**
- Driver package mount/extract stage: **PASS**
- Actual driver installation completed: **PASS**
- Completion button clicked: **PASS**
- AutoIt error after completion: **NONE**
- User report: normal installation completed successfully

This specifically closes the highest-risk regression from the earlier 26v4 optional V1.0 post-build path, where the completion event exposed malformed/unknown AutoIt tokens.

The 26v5 build deliberately ports the verified Base CLEAN logic and did not append the problematic 26v4 V1.0 cleanup function.

## Evidence

Screenshots supplied by the user show:

1. Korean 26v5 main UI after successful hardware scan, including detected GPU, audio, network adapter and mainboard devices.
2. Korean driver-install progress UI with initialization completed and driver package mount/extract stage running.

The user then explicitly confirmed that the installation completed and clicking the completion button produced no error.

## Remaining final-release gate

Before labeling the build FINAL, verify once after the install/reboot cycle:

- legitimate `UnmountDrv` cleanup completes normally
- no unexpected `SoftInst` RunOnce entry remains/appears
- no `C:\SoftInst` residue
- no unexpected `inst.vbs` / `inst.cmd` / `wget.exe` residue
- Edge homepage/startup/profile settings were not modified by EDv9
- normal driver state remains intact after reboot

## Status

**WINDOWS INSTALL + COMPLETION BUTTON: PASS**

**FINAL RELEASE: POST-REBOOT / NO-RESIDUE CONFIRMATION PENDING**
