# EDv9 26v5 KO CLEAN ISO GUARD — 최종 제작 및 격리 VM 검증 (2026-11-25)

## 결과
**EDv9 26v5 실행파일에 26v4 팝업 2개를 네이티브 AutoIt 본체 코드로 이식하고, ISO 전체 원시 데이터 SHA-256을 검사하는 완성 ISO의 정상/변조 실행 분기 검증 PASS.**

단일 네이티브 `EDv9_x64_KO_CLEAN.exe` 내 기능 구현이며 별도 보정기·런처 없음. 26v4/26v5 원본 마스터 변경 없음.

## 배포 파일 (SoNG-HoME)
- 파일: `D:\SoNG-HoME_Admin\SoNG_Admin\Downloads\EDv9_26v5_KO_CLEAN_ISO_GUARD_FINAL_20261125.iso`
- 크기: **11,954,364,416바이트**
- 배포 ISO 전체 SHA-256 (원본 파일 바이트 그대로): **`690B9F60B96B55A4A6C67032A5A0F99C899D4303224C749A4223B3C131327FC7`**
- ISO 내 `EDv9_x64_KO_CLEAN.exe` SHA-256: **`A4ACB5A329AAFD7CBE0FE004E156A738F3CF705EE7CE9C7526631C6D247FBD5E`**
- 검사에 사용한 정규화 SHA-256 (EXE 내부 H=64자리만 '0'으로 정규화): **`8DE3A066C893742E1CBD7C564D52268AE0CCAF269E5B8C70D2D2609842C27BC8`**
- ISO 루트: `EDv9_x64_KO_CLEAN.exe`, `EDv9_x64.ini`, `EDv9_v9.0.2609.20009.dat`, `Drivers\`; 총 106 파일.
- UDF 1.02, 기존 CLEAN/OFFLINE 한글화 기능 유지.

## 원본 직접 대조
- **26v5 최종 기준 EXE** SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`; AutoIt 24,069 토큰 라인 보존.
- **26v4 팝업 기준 EXE** SHA-256: `2A36250601AB18CCC62B563744A69715F6D10C37B5B1B9CEB7E9E9AD96710A52`.
- 26v4 실제 제작자/보안안내 MsgBox 호출 2개를 토큰 단위로 복사하고 제목의 버전만 26v5로 변경. 새 통합 코드 24,202 토큰 라인.
- 기존 정규 26v5 `EDv9_26v5_KO_CLEAN_FINAL.iso` 원본 및 26v4 기준 EXE 변경하지 않음.

## ISO 무결성 방식
- EXE를 ISO에서 실행할 때 `GetDriveTypeW=DRIVE_CDROM` 확인. 일반 폴더로 복사한 EXE 단독 실행은 차단 대상으로 설계.
- `CreateFileW('\\.\<드라이브>:')`를 통한 마운트 DVD 원시 데이터 **전 구간**을 4MiB 버퍼로 읽고 Windows BCrypt SHA-256 증분 계산.
- ISO 본문과 프로그램이 자신을 서로 참조하는 문제를 해결하기 위해 PE 내 고유 `EDV9_ISO_SEAL_V1` 레코드의 **H=64바이트 영역만** '0'으로 정규화한 뒤 비교. O에는 marker 시작 위치, H에는 O+57 위치를 사용.
- 일반 파일 수정·삭제·추가뿐 아니라 동일 크기 1바이트 수정도 검출. 고의적인 실행파일 역패치·재봉인까지 수학적으로 막는 디지털 서명 방식은 아니며 출처 인증 강화를 위해 별도 서명 체계가 필요할 수 있음.
- ISO 전체를 검사하므로 실행 시간이 파일 크기에 비례해 늘어날 수 있음.

## 구현 과정의 오류 수정 (최종 반영)
- V1 검증 후 버퍼드 원시 DVD I/O로 변경(임의 메모리 정렬 요구 회피).
- V2는 **정상 ISO도 오류 코드 10으로 거부**. 원인: O(marker 시작)를 정규화 오프셋으로 잘못 사용, 실제 64바이트 H는 O+57. 코드 수정 후 V3 재컴파일/재봉인.
- Windows BCrypt 알고리즘 known-answer SHA-256(`abc`) PASS.
- 같은 AutoIt 코드로 실제 완성 ISO 11,954,364,416바이트 전체를 파일 및 격리 VM의 원시 DVD에서 각각 계산했을 때 `A502CEF1...` (V2 QA 해시) 일치 확인. 최종 V3 빌드도 자체 정규화/전체 SHA 체크 PASS.

## 실가동 VM PASS
격리 Hyper-V VM: `EDv9_26v5_ISO_GUARD_QA_20261125`, Win11, 네트워크 미연결, 독립 VHDX, 관리자 UAC 승인도 **게스트 가상 마우스에만** 전달. 호스트/주력 VM Windows·BCD·드라이버 미변경.

**정상 V3 ISO**: 실행 → ISO 검사 통과 → 26v4에서 이식한 `EDv9 26v5 한글패치 V1.0` 팝업 표시 → `EDv9 26v5 CLEAN OFFLINE 보안 안내` 팝업 표시 → 26v5 `ITSK 만능 드라이버 - 26v5 표준 버전` 메인 화면 표시 **PASS**.
- `VM_QA\V3_Positive_CreatorPopup_PASS.png`
- `VM_QA\V3_Positive_SecurityPopup_PASS.png`
- `VM_QA\V3_Positive_MainUI_PASS.png`

**변조 V3 ISO**: 정상 ISO의 `EDv9_x64.ini` 원시 데이터 **868,372 위치의 1바이트 0x0A→0x0B** 수정; 원래 파일 크기 11,954,364,416바이트 그대로. 정적 normalized SHA 불일치 **FAIL(예상 동작)**; 격리 VM 직접 실행 시 원래 두 안내 팝업 이전에 `EDv9 26v5 ISO 무결성 오류 / 오류 코드: 10`로 실행 차단 **PASS**.
- `VM_QA\V3_Negative_OneByteTamperBlocked_PASS.png`
- `VM_QA\V3_tamper_proof.json`

**미검증 범위**: 실제 드라이버 설치/변경, 모든 Windows 버전 및 타사 ISO 편집기의 변조 시나리오. VM에서 설치 버튼은 누르지 않음. 관리자 UAC 승인은 기존 네이티브 프로그램과 동일하게 필요.

## 재검증 및 배포 주의
1. ISO 파일 그대로 Windows에서 **마운트**한다.
2. 가상 DVD 드라이브 내부의 `EDv9_x64_KO_CLEAN.exe`를 실행한다. 바깥으로 추출하면 보안 검사에서 차단된다.
3. 보안 검사 → 제작자 안내 → CLEAN 보안 안내 순서를 확인한다.
4. ISO를 조금이라도 다시 편집/저장하면 해시 불일치로 실행이 중단된다.
5. **동일한 파일명을 사용해 기존 정품/기준 ISO를 덮어쓰지 말 것**. 배포 ISO와 SHA 값을 같이 보관한다.

## 소스
- [네이티브 가드](../tools/26v5/edv9_native_iso_guard.au3)
- [EXE+ISO 빌드 및 봉인](../tools/26v5/build_26v5_raw_iso_seal.py)
- [격리 VM 초기 QA 스크립트](../tools/26v5/edv9_iso_guard_vm_qa.au3)

