# EDv9_KOR

EDv9 / 万能驱动9 한국어 CLEAN OFFLINE 패치 프로젝트입니다.

## 목표

- 전체 UI 한국어화
- 긴 한글 문구 자연스럽게 축약
- 드라이버 검색/매칭/설치 기능 유지
- Edge/브라우저 설정 변경 제거
- SoftInst / wget / inst.cmd / inst.vbs 제거
- ITSK 외부 통신 및 중국 포털 후처리 제거
- UnmountDrv 등 정상 드라이버 정리 기능 유지
- 설치 후 찌꺼기 없는 No-Residue 구조
- 설정값 영구 저장 지원
- 최종 배포는 가능한 한 원클릭 패처 1개

핵심 원칙:

> 오프라인 드라이버 설치 기능만 남긴 한국어 CLEAN 버전

## 현재 기준

현재 기준 작업선은 EDv9 26v5 / 9.0.2609.20009 Korean CLEAN OFFLINE No-Residue입니다.

대용량 원본 드라이버 패키지와 제3자 저작물은 Git 히스토리에 직접 포함하지 않습니다. 저장소에는 분석 기록, 해시, 패치 로직, 재현 가능한 빌드/검증 자료를 중심으로 관리합니다.

현재 작업 상태는 [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md)를 참고하세요.

## FINAL release

EDv9 26v5 / 9.0.2609.20009 Korean CLEAN OFFLINE No-Residue + Settings Persistence

- FINAL EXE SHA-256: `12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA`
- Settings persistence: Windows runtime PASS
- Driver package-mode persistence: Windows runtime PASS
- Scan / driver-list path: Windows runtime PASS
- Previous critical install/completion/cleanup paths: byte-identical preservation from multi-PC runtime-verified FINAL
- Blog / usage guide: https://blog.naver.com/shj2564/224426811365

### ISO status

The previously published ISO SHA-256:

`F660C0A32E98ECCDDBEABF744B9FB380807F8C42F34551773A19DCD1F33D8261`

belongs to the **previous FINAL EXE** (`955E845C...`) and must not be represented as containing the new settings-persistence FINAL.

A new canonical ISO hash is **pending rebuild** with the new FINAL EXE.
