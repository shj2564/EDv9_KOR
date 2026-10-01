# EDv9 26v5 settings persistence analysis — 2026-10-01

## Report

Feedback: In Settings, changing **Driver install after** from automatic restart to manual restart wait and clicking **Apply settings** does not persist after the program is restarted. The same behavior occurs after copying the ISO contents to a writable normal folder.

## Directly analyzed inputs

- Original 26v5 core executable SHA-256: `C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86`
- FINAL Korean CLEAN executable SHA-256: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`
- Original INI SHA-256: `608E193A2B03A13C4F657F89A15B43CC40437906901DF8623B21FBA18775CCF2`

The original and FINAL AutoIt EA06 scripts were decoded and the settings path was compared at token-line level.

## Root cause

This is not an ISO write-protection issue and is not caused by the Korean CLEAN code neutralization.

EDv9 26v5's original Settings UI applies these values to **runtime variables for the current process only**. It does not persist the GUI selections to the adjacent INI or registry.

The adjacent `EDv9_x64.ini` contains only:

```ini
[Config]
DisplayVersion = "26v5"
OSSupport = "Win11.x64, Win10.x64"
```

The only INI reads in the recovered original script read optional `TempDir` and `DriversDir` values. There is no `IniWrite` path for `Extract` or `NeedReboot`.

## Reboot setting flow

Relevant internal keys and original/final UI strings:

| XQS | Original | Korean FINAL |
|---:|---|---|
| 2826 | `NeedReboot` | unchanged |
| 3460 | `Reboot` | unchanged |
| 2172 | `全部安装完成后自动重启\|等待手动重启` | `모두 설치한 후 자동 재시작\|수동 재시작 대기` |
| 4344 | `手动重启` | `수동 재시작` |
| 1916 | `应用设置` | `설정 적용` |

On each process start, `NeedReboot` is initialized from command-line/runtime conditions:

- `/NoReboot`
- `/nr`
- Deploy mode

Without the no-reboot conditions, the default is automatic reboot.

Opening Settings creates a temporary map containing current `WinDirs`, `DestWinDir`, `Extract`, and `NeedReboot`. Clicking Apply calls the settings-apply routine, which updates the current runtime variables and returns to the main page. No persistence write follows.

## Korean translation integrity

The two translated strings used by the runtime substring tests remain internally consistent:

- Extract option contains `마운트`; test needle is `마운트`.
- Manual reboot option contains `수동 재시작 대기`; test needle is `수동 재시작`.

Therefore the Korean string replacement does not break the current-session selection logic.

## Exact code-preservation check

The complete raw token bytes of the following settings-related functions are byte-identical between original 26v5 and FINAL after accounting for the two early cleanup-registration lines added by the FINAL build:

| Function | Result |
|---|---|
| `HLNHLMJXGDXU` — Apply values | byte-identical |
| `TODJKXDXBOWQ` — Settings UI creation | byte-identical |
| `OUXMGLYTXYIT` — Settings button event | byte-identical |
| `MOVCSCOEDAKE` — Settings UI initialization | byte-identical |
| `QUYIDUAOHFKA` — Main event loop/settings transition | byte-identical |

This rules out the Korean/CLEAN patch altering the original save behavior in these paths.

## Conclusion

**Confirmed:** EDv9 26v5 original behavior is session-only **Apply**, not persistent **Save**.

The Korean label `설정 적용` is semantically correct for the Chinese original `应用设置`. The usage-guide wording that said clicking it would "save" the setting should be corrected.

## Optional enhancement

If persistent preferences are desired in the Korean CLEAN build, implement them as a new explicit feature rather than treating this as a regression fix. Recommended design:

- Sidecar section/file owned by the Korean patch, separate from vendor metadata.
- Persist only user-facing preferences such as `Extract` and `NeedReboot`.
- Preserve command-line overrides (`/NoReboot`, `/nr`, `/Extract`, `/x`) as higher priority.
- Fail safely to original defaults if the preference file is absent/corrupt.
- Do not touch driver matching/install or CLEAN neutralization paths.
