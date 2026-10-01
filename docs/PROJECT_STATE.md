# PROJECT STATE

Last updated: 2026-10-01 KST

## Project target

EDv9 / 万能驱动9를 한국 사용자용 **Korean CLEAN OFFLINE No-Residue** 버전으로 유지한다.

### 반드시 유지
- DAT 로딩/검증
- HWID 검색
- 하드웨어 스캔
- 드라이버 매칭
- INF 설치
- 7-Zip
- 드라이버 WIM
- 패키지 마운트/압축 해제
- UnmountDrv
- 정상 재부팅/정리 경로

### 제거/차단 대상
- Edge/브라우저 설정 변경
- SoftInst
- wget.exe
- inst.cmd
- inst.vbs
- 불필요한 ITSK 외부 통신
- 123.itsk.com / api.itsk.com 후처리
- 2345 / 360 포털 연결 및 설정 변경

## 26v2 baseline

Version: 9.0.2605.20006

Original EXE SHA-256:
`2D942FCD0CA4F798D8D3330EB3243F6CE34A212EB3CC7BC8058B6674662D4975`

Original DAT SHA-256:
`B54A265D0A07737A5F82B75408DC1ED492FC3EC97EB53D5C4350692BE0C11A40`

AutoIt EA06 x64 / SKAEv2 계열이며 SCRIPT는 일반 위치가 아닌 0x28부터 시작하는 구조로 분석되었다.

## 26v4 baseline

Version: 9.0.2608.20008

Original EXE SHA-256:
`FD2D3098A42B0922D4E17D159C16D313DC01EDDFDA67EF3AA5B11FD58852CDF2`

Original DAT SHA-256:
`2862354AEA4EB54F7E51BBE721A0E58EED0DF8611E0F80BCDE7290A97503AAF8`

CLEAN/Hangul 이식 결과:
- XQS 4,940 구조 유지
- 26v2 최종 변경 420개 중 419개 매핑
- 한글 포함 변경 388개
- CLEAN/non-Hangul 변경 31개
- 남은 CJK 150개는 시간대/내부 데이터
- 사용자 노출 예상 밖 CJK 0
- UnmountDrv 유지

26v4 Base CLEAN EXE SHA-256:
`6D0F312376C6389E6F118E69F46F2581FE8F898BD9A9D897AEF5178C3705C85D`

Completion HOTFIX candidate:
`EDv9_x64_Ko.exe`

SHA-256:
`D3B46ABBC6D64BC07149682B6F1A60722356AE6C685EE63B9645C458A6C38086`

Completion HOTFIX는 Line 24023/24025의 lowercase `@error` 토큰을 canonical `@ERROR`로 교체한 상태다.

### 26v4 남은 런타임 확인

Windows 실제 환경에서:
1. 드라이버 검색
2. 설치
3. 완료 버튼 클릭

후 더 이상 AutoIt Error / Unknown macro가 발생하지 않는지 최종 확인한다.

## 26v5

Verified public version information:
- Release line: 26v5
- Internal version: **9.0.2609.20009**
- Changelog date: **2026-09-24**
- Public mirror pages observed: 2026-09-28 ~ 2026-09-29
- Software change note: stable release minor adjustment (稳定版微调)

### Direct mirror confirmed in real use

2026-09-29 사용자 브라우저에서 아래 **직접 HTTP/HTTPS 파일 미러가 실제 다운로드 중인 것을 확인**:

`https://152.136.103.177:5245/cu/IT天空资源分流/万能驱动/万能驱动9/EDv9_26v5.zip`

Observed from browser:
- File: `EDv9_26v5.zip`
- Displayed size: about **9.51 GB**
- Download completed successfully
- This route is preferred over Quark/Baidu/123Pan when the latter require payment or throttled app workflows

### Original archive baseline

File:
`EDv9_26v5.zip`

SHA-256:
`62A131570E3C33FEF76236C69D6B8DD24406CBE5FD6F62DAE187545A0C11BE43`

Status:
- Original ZIP acquired ✅
- Archive hash recorded ✅
- EXE/DAT/INI/@version extracted ✅
- Original EXE SHA-256: `C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86`
- Original DAT SHA-256: `A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D`
- AutoIt EA06 SCRIPT recovery ✅
- recovered source: 24,031 lines
- XQS: 4,940 entries
- CJK strings: 538 = time/zone internal 150 + other 388
- SoftInst / wget / inst.cmd / inst.vbs present
- 123.itsk.com / api.itsk.com present
- 2345 / 360 portal strings present
- Edge msedge / homepage / startup_urls / restore_on_startup / PrefsLightweight paths present
- UnmountDrv present and must be preserved
- 26v4 vs 26v5 binary/token/XQS diff: next

Download/mirror references observed on 2026-09-29:
- Direct file mirror: https://152.136.103.177:5245/cu/IT天空资源分流/万能驱动/万能驱动9/EDv9_26v5.zip
- Puresys mirror page: https://www.puresys.net/1147.html
- Puresys 123Pan shared folder: https://www.123pan.cn/s/1QeA-4fVrv
- Puresys Baidu share: https://pan.baidu.com/s/1X4rnmDzgLsnLrj6XDbazsA?pwd=vijn
- 4MF mirror page: https://www.4mf.net/47835.html
- 4MF Quark share: https://pan.quark.cn/s/52492e99907f
- 4MF Baidu share: https://pan.baidu.com/s/1AaCICasQHFiZhsIBO3KIWw?pwd=88in
- 4FB listing also shows ITSK 驱动_26v5 官方26年09月版 on 2026-09-29, but its individual article/download URL was not yet indexed during verification.

### 26v5 작업 순서

1. 원본 ZIP/S7Z 확보 ✅
2. 전체 패키지 SHA-256 ✅
3. EXE/DAT/INI/@version 안전 추출
4. EXE/DAT SHA-256
5. PE / AutoIt EA06 / SCRIPT offset 확인
6. XQS 구조 확인
7. 26v4 함수/문자열/token diff ✅
8. DAT 바인딩 구조 확인
9. SoftInst / wget / inst.cmd / inst.vbs 확인
10. Edge/브라우저 조작 코드 확인
11. ITSK/123/2345/360 관련 네트워크 경로 확인
12. UnmountDrv 정상 경로 분리 확인
13. 기존 한국어 UI 이식 ✅
14. 신규 문자열 번역 및 길이 조정 ✅ (신규 CJK UI 0)
15. CLEAN OFFLINE neutralization ✅
16. 바인딩 검증 ✅ (원본 DAT 유지, hash-mismatch return only neutralized)
17. No-Residue 패처 ✅ (TEST)
18. Windows 실사용 테스트 ✅ (설치 + 완료 버튼 PASS)
19. 배포 기준 SHA-256 확정 ✅

## Repository policy

- 메뉴 자체는 임의 삭제하지 않는다.
- UI 잘림은 자연스러운 축약으로 처리한다.
- 드라이버 핵심 기능은 보존한다.
- CLEAN 대상은 단순 UI 숨김보다 실행 경로 제거/무력화를 우선한다.
- 원본 복원 가능성을 유지한다.
- 패치 배포 파일 수는 최소화한다.
- 임시/백업 찌꺼기는 종료 후 제거한다.
- 대용량 원본 패키지 및 드라이버 DB/WIM은 Git 히스토리에 직접 넣지 않는다.
\n\n### 26v5 Korean CLEAN candidate\n\n- 26v5 Korean CLEAN candidate build ✅
- Candidate EXE SHA-256: `40D5155F455260AC750B65BA80499B8C88673C3DCA18EAA750C26D238A886D89`
- Candidate size: 17,870,872 bytes
- Patched token SHA-256: `625608E90CD49C9E45623882FDAD9C4271D72C60212CBE73BAA5F07FEC5FEA59`
- 419/419 XQS replacements verified
- CLEAN code neutralization 10/10 verified
- Remaining CJK 150/150 = timezone/internal records
- UnmountDrv retained
- Core PE .text/.rdata/.data/.pdata/.reloc byte-identical
- TEST one-click patcher SHA-256: `C1B02DCDDA0A509329D788297FF9B7C64BC55ECAF10DC092E1A8520C936FF0B9`\n- TEST patcher additionally verifies full Drivers folder + `Drivers/@version` SHA-256 before applying
- Detailed verification: `docs/EDv9_26v5_KOREAN_CLEAN_STATIC_VERIFICATION.md`
- Status: **WINDOWS INSTALL + COMPLETION BUTTON PASS / POST-REBOOT NO-RESIDUE CHECK PENDING**
- Windows launch → Korean UI → scan → install → completion button: **PASS**\n- Remaining FINAL gate: reboot/UnmountDrv cleanup + SoftInst/Edge no-residue confirmation\n- Runtime evidence: `docs/EDv9_26v5_WINDOWS_RUNTIME_20260930.md`\n

### 26v5 post-install residue check

User verification on Windows:
- `Test-Path C:\SoftInst` -> `False`
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce` -> no SoftInst/inst.vbs entry shown
- SoftInst/RunOnce no-residue: **PASS**

Remaining residue observed:
- `C:\Drivers` remained after the successful install test.

Safe cleanup HOTFIX candidate:
- EXE SHA-256: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`
- Size: 20,427,288 bytes
- Token SHA-256: `C2FE0C9D5FBA4A43697A81798710C0A164E5EB1BEB62E66B494EBCB15A9F6861`
- Uses exact token bytes from the 26v4 final Completion HOTFIX for the safe `C:\Drivers` cleanup handler.
- Does not delete a pre-existing `C:\Drivers` folder.
- Does not delete while RunOnce `UnmountDrv` is pending.
- Otherwise removes `C:\Drivers` recursively on normal AutoIt exit.
- Static verification: **PASS**
- Runtime cleanup test: **PASS**
- Verification: `docs/EDv9_26v5_DRIVERS_CLEANUP_HOTFIX_STATIC_VERIFICATION.md`


### 26v5 FINAL

Runtime-verified FINAL baseline:

- Final EXE: `EDv9_x64_KO_CLEAN.exe`
- Final EXE SHA-256: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`
- Final size: 20,427,288 bytes
- Final No-Residue one-click patcher SHA-256: `D85D67349288B0902ED848485E5DE900FEB36A49A6AED79A1714A1D257D86D2E`
- Windows launch/UI/scan/install/completion: PASS
- SoftInst/RunOnce residue: PASS (none)
- C:\Drivers automatic cleanup: PASS
- Existing C:\Drivers protection: implemented
- UnmountDrv pending cleanup protection: implemented
- Detailed final runtime report: `docs/EDv9_26v5_FINAL_RUNTIME_20260930.md`

Status: **FINAL RUNTIME VERIFIED**


### 26v5 FINAL ISO builder

- One-click builder prepared: `EDv9_26v5_FINAL_Make_ISO_OneClick.cmd`
- Builder SHA-256: `D1823828CE8307251F5DB7DEF3C9B7A01083B3E3693FDF42A952AEBE21B477DE`
- Repository source: `tools/26v5/make_final_iso.ps1`
- Output: `EDv9_26v5_KO_CLEAN_FINAL.iso`
- Filesystem: UDF 1.02
- Volume label: `EDv9_26v5_KO`
- Original `EDv9_x64.exe` excluded
- FINAL EXE is the only EXE in ISO
- ISO is automatically mounted and verified after creation
- ISO SHA-256 + build report are generated automatically
- Actual ISO SHA-256: pending local build on the Windows machine containing the complete Drivers set


### Cross-PC runtime verification

2026-09-30 user confirmed the FINAL build also works normally on another Windows PC.

Result:
- launch: PASS
- Korean UI: PASS
- scan: PASS
- driver workflow: PASS
- general runtime: PASS

This confirms the FINAL build is not limited to the original test PC.

Official blog / release guide:
https://blog.naver.com/shj2564/224426811365

Canonical FINAL hashes:
- EXE: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`
- ISO: `F660C0A32E98ECCDDBEABF744B9FB380807F8C42F34551773A19DCD1F33D8261`
- No-Residue patcher: `D85D67349288B0902ED848485E5DE900FEB36A49A6AED79A1714A1D257D86D2E`

Final status:
**EDv9 26v5 Korean CLEAN OFFLINE No-Residue — MULTI-PC RUNTIME VERIFIED FINAL**


### 26v5 Settings Persistence HOTFIX candidate — 2026-10-01

Direct analysis confirmed the original 26v5 Settings screen applies `Extract` / `NeedReboot` only to the current process and does not persist them.

A new Korean CLEAN persistence HOTFIX candidate has been built from the canonical FINAL baseline.

- Base FINAL SHA-256: `955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713`
- Candidate SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`
- Candidate size: 22,985,240 bytes
- Candidate token SHA-256: `8FB9D574B1D29A18DA56D344DEF63EDF51E106765579169579528D46CF164624`
- Token lines: 24,069
- Persistence store: `HKCU\Software\SoNG\EDv9_KOR`
- Persisted values: `Extract`, `NeedReboot` (REG_DWORD)
- Target Windows directory remains auto-detected and is not persisted.
- `/Extract`, `/NoReboot`, `/nr`, and deploy no-reboot precedence preserved.
- Original 24,042 FINAL token lines preserved byte-for-byte, with two call-site insertions plus 25 helper lines.
- Existing CLEAN / UnmountDrv / C:\Drivers cleanup / driver-install paths preserved.
- PE static verification: PASS.
- 36-case preference/override truth-table simulation: PASS.
- Detailed report: `docs/EDv9_26v5_SETTINGS_PERSISTENCE_HOTFIX_STATIC_VERIFICATION.md`

Status: **SETTINGS PERSISTENCE RUNTIME PASS / FULL REGRESSION GATE PENDING**

2026-10-01 Windows runtime confirmation:
- Settings → `수동 재시작 대기` → `설정 적용` → exit → relaunch
- `수동 재시작 대기` remained selected after relaunch: **PASS**
- Runtime evidence: `docs/EDv9_26v5_SETTINGS_PERSISTENCE_RUNTIME_20261001.md`

The previous MULTI-PC RUNTIME VERIFIED FINAL hash remains canonical until the persistence candidate passes the remaining package-mode/override and normal driver-flow regression checks.


### 26v5 Settings Persistence FINAL promotion — 2026-10-01

User-confirmed Windows runtime:
- Driver install-after preference persistence: **PASS**
- Driver package-mode preference persistence: **PASS**
- Hardware scan: **PASS**
- Driver-list path: **PASS** (test machine had no pending installable drivers because they were already installed)

Change-impact verification:
- The persistence patch only adds preference load/save calls and helper functions.
- Actual driver install, completion button, UnmountDrv, CLEAN OFFLINE neutralization, and safe C:\Drivers cleanup remain byte-identical to the prior multi-PC runtime-verified FINAL implementation.
- Those untouched paths were not re-executed on this exact candidate during the 2026-10-01 session; their confidence is inherited from exact-code preservation + previous runtime PASS.

New canonical FINAL EXE:
- File: `EDv9_x64_KO_CLEAN.exe`
- SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`
- Size: 22,985,240 bytes
- Token SHA-256: `8FB9D574B1D29A18DA56D344DEF63EDF51E106765579169579528D46CF164624`
- Settings store: `HKCU\Software\SoNG\EDv9_KOR`
- Persisted values: `Extract`, `NeedReboot`

Status:
**FINAL EXE PROMOTED — SETTINGS PERSISTENCE RUNTIME VERIFIED**

ISO note:
- Previous ISO SHA-256 `F660C0A32E98ECCDDBEABF744B9FB380807F8C42F34551773A19DCD1F33D8261` contains the previous FINAL EXE `955E845C...`.
- A new ISO must be rebuilt before assigning a new canonical ISO hash for the settings-persistence FINAL.


### 26v5 Settings Persistence FINAL ISO — 2026-10-01

Canonical FINAL ISO build completed and mounted validation passed.

- ISO: `EDv9_26v5_KO_CLEAN_FINAL.iso`
- SHA-256: `6AD8DC770FDDB2E27782131B6A2AB4F48C66BB66416C51AE8856EE549C96B536`
- Size: 11,951,794,176 bytes
- Payload file count: 106
- Payload bytes: 11,950,815,374
- Filesystem: UDF 1.02
- Volume label: `EDv9_26v5_KO`
- Build time: 2026-10-01 19:02:16 KST
- Validation: PASS
- FINAL EXE inside ISO: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`

The prior ISO hash `F660C0A32E98ECCDDBEABF744B9FB380807F8C42F34551773A19DCD1F33D8261` is superseded.

Final documentation image was also regenerated using the actual Settings UI screenshots and corrected Korean option labels.

Canonical status:
**EDv9 26v5 Korean CLEAN OFFLINE No-Residue + Settings Persistence — FINAL ISO VERIFIED**

Release snapshot:
`docs/EDv9_26v5_FINAL_SETTINGS_SAVE_RELEASE_20261001.md`
