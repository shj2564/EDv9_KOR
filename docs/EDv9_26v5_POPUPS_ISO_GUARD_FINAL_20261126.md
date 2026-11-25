# EDv9 26v5 한글 CLEAN — 원본 26v4 팝업 + ISO 전체 무결성 봉인 FINAL

확정: 2026-11-26 00:03 KST

## 공식 새 배포 파일
- 파일: `EDv9_26v5_KO_CLEAN_ISO_GUARD_FINAL_20261126.iso`
- 위치(SoNG-HoME): `D:\SoNG-HoME_Admin\SoNG_Admin\Downloads\EDv9_26v5_KO_CLEAN_ISO_GUARD_FINAL_20261126.iso`
- ISO 크기: **11,954,364,416 bytes**
- **실제 파일 SHA-256:** `5BBC9660344BC655D0255DE0DADE2B365C1D0FFE598144B18D6DBD0189C10803`
- ISO 무결성 검사 내부 정규화 SHA-256: `B614C5B41726545BC49BEFF71807E64A59518DEC417A4B06E190932A79D50166`
- 내부 실행파일: `EDv9_x64_KO_CLEAN.exe`, SHA-256: `E43E8EEFBB03E6B85621B9A472A7EFF4679CF23952C710876558D84F849CBE12`
- DAT SHA-256: `A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D`
- INI SHA-256: `608E193A2B03A13C4F657F89A15B43CC40437906901DF8623B21FBA18775CCF2`
- Drivers/@version SHA-256: `3C6923B48808D1B04B1280B447B7053F5CC8987EDCF1714B0FA1C83F422B633F`
- UDF 1.02 / 볼륨 `EDv9_26v5_KO` / 파일 106개 / 내부 EXE 1개
- 체크섬: 위 ISO 옆의 `EDv9_26v5_KO_CLEAN_ISO_GUARD_FINAL_20261126.iso.sha256.txt`

## 구현 사항
1. 검증된 26v5 SettingsSave 최종 EXE SHA-256 `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`를 기준으로 사용.
2. 실제 26v4 팝업 원본 EXE SHA-256 `2A36250601AB18CCC62B563744A69715F6D10C37B5B1B9CEB7E9E9AD96710A52`의 AutoIt 토큰 팝업 두 줄을 보존해 삽입(제목 버전만 26v5로 수정).
3. 독립 런처·사후 보정기 없음. 원본 EDv9 네이티브 EXE 내부에서 시작 시 ISO 전체 검증.
4. Win32 CD-ROM 장치(마운트된 ISO)에서 ISO raw 전체 바이트를 SHA256로 계산하고, 내장 봉인값과 비교. 봉인 필드 64바이트만 정규화하여 자기참조 문제를 해결.
5. 파일 내용 변경/추가/제거, ISO 파일시스템 구조 변경, ISO 길이 변경, ISO 밖으로 EXE 복사 실행 시 **차단하도록 설계**.
6. 정상은 팝업 2개 후 원래 EDv9 메인 화면으로 계속 진행; 실패는 `EDv9 26v5 ISO 무결성 오류`로 중지.
7. ISO 전체 해시 검사는 약 12GB의 모든 바이트를 읽으므로 PC/저장장치 속도에 따라 시작이 지연될 수 있음.

## 실제 격리 VM QA — PASS
VM: `EDv9_26v5_ISO_GUARD_QA_20261125` (Windows 11, Hyper-V, 네트워크 미연결), 테스트 후 Off.
- 정상 새 V4 ISO: 첫 안내 `EDv9 26v5 한글패치 V1.0` 표시, 두 번째 `EDv9 26v5 CLEAN OFFLINE 보안 안내` 표시, 정상 메인 GUI 진입.
- `VM_QA\V4_final_runtime_POSITIVE.log`: `FINAL PASS=True CREATOR=True SECURITY=True GUARD_DENIED=False MAIN=True`, 종료코드 `0`.
- 변조 ISO: 원본 V4 ISO의 UDF `EDv9_x64.ini` 데이터 위치 868372의 **1바이트**만 10→11로 변경, 전체 ISO 크기 불변.
- 정적 변조 SHA 검사: `Raw ISO digest mismatch`로 거부.
- 실제 변조 ISO Windows VM 실행: 제작자/보안 팝업 출력 **이전**에 `EDv9 26v5 ISO 무결성 오류` 표시, 코드 10, 실행 중지.
- `VM_QA\V4_runtime_NEGATIVE.log`: `FINAL PASS=True CREATOR=False SECURITY=False GUARD_DENIED=True MAIN=False`, 종료코드 `0`.
- 화면 증거: `VM_QA\V4_after_UAC_screen.png`, `V4_Security.png`, `V4_MainUI.png`, `V4_Tamper_runtime.png`.
- 직접 ISO 마운트 검사: 파일 106개, EXE 1개, DAT/INI/@version/EXE SHA-256 전부 작업본과 일치.

## 사용방법
Windows 파일 탐색기에서 위 ISO 마운트 → 가상 DVD 드라이브 안의 `EDv9_x64_KO_CLEAN.exe`를 **관리자 권한**으로 실행 → ISO 전체 무결성 진행 표시 → 제작자/보안 팝업 확인 → 드라이버 화면.
ISO의 EXE를 C: 등에 복사한 단독 실행은 차단되는 것이 의도된 동작. ISO 또는 내부 파일 수정 후 실행도 차단됨.

## 제한사항
- 검증 범위는 Windows 11 격리 VM에서 ISO 정상 실행/변조 차단까지. 수정본으로 실제 드라이버 설치 전 과정을 새로 실행하지는 않았음. 이전 26v5 CLEAN/SettingsSave 드라이버 경로 코드는 보존됨.
- SHA-256 자체 검사만으로 **검사 코드까지 수정하고 ISO를 재봉인할 수 있는 고급 공격자**를 원천 차단할 수는 없음. 그런 위협까지 막으려면 별도 비밀키 기반 서명/공인 서명 검증 및 신뢰체인이 필요함.
- 원래 2026-10-01의 `EDv9_26v5_KO_CLEAN_FINAL.iso` 및 기존 확정 EXE는 수정/삭제하지 않았음.

## 소스
`tools/26v5/build_26v5_raw_iso_seal.py`
`tools/26v5/edv9_native_iso_guard.au3`
`tools/26v5/edv9_iso_guard_vm_qa.au3`
