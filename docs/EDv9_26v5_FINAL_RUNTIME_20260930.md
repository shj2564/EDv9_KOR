# EDv9 26v5 Korean CLEAN OFFLINE — No-Residue Runtime PASS

Date: 2026-09-30 KST

## Tested build

Final candidate executable SHA-256:

`955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`

Size: 20,427,288 bytes

## Windows cleanup test

User performed the explicit C:\Drivers cleanup runtime test:

1. Confirmed/removed any pre-existing `C:\Drivers`.
2. Launched the DriversCleanup build.
3. Created:
   - `C:\Drivers`
   - `C:\Drivers\cleanup_test.txt`
4. Confirmed `Test-Path "C:\Drivers"` returned `True`.
5. Closed EDv9 normally.
6. Confirmed `Test-Path "C:\Drivers"` returned `False`.

Result:

**C:\Drivers automatic cleanup: PASS**

## Previous runtime gates already passed

- Program launch: PASS
- Korean UI: PASS
- Hardware scan: PASS
- Driver list: PASS
- Actual driver installation: PASS
- Completion button: PASS
- AutoIt completion error: NONE
- `C:\SoftInst`: False
- RunOnce SoftInst/inst.vbs entry: absent
- UnmountDrv legitimate cleanup path retained

## Cleanup safety design

The cleanup handler:
- does not delete a `C:\Drivers` directory that existed before EDv9 launch
- skips deletion when legitimate RunOnce `UnmountDrv` cleanup is pending
- otherwise removes a `C:\Drivers` directory created during this EDv9 session on normal AutoIt exit
- uses the exact corrected token bytes from the 26v4 Completion HOTFIX for the cleanup function, including valid Func identifier opcode and canonical `@ERROR` macro spelling

## Final promotion

The executable above is promoted to the **EDv9 26v5 Korean CLEAN OFFLINE FINAL baseline**.

Final EXE SHA-256:

`955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`

Final one-click No-Residue patcher SHA-256:

`D85D67349288B0902ED848485E5DE900FEB36A49A6AED79A1714A1D257D86D2E`

Status:

**FINAL RUNTIME VERIFIED**
