# EasyDrv9 (EDv9) 26v5 한글판 — SoNG Korean CLEAN OFFLINE

**EasyDrv9 한글화 · 만능드라이버9 한국어판 · EDv9 26v5 Korean CLEAN OFFLINE / No-Residue**

> **[제작자 SoNG 공식 블로그 — EasyDrv9 26v5 한글판 소개와 사용 방법](https://blog.naver.com/shj2564/224426811365)**  
> 처음 사용하시는 분은 블로그의 설명을 먼저 확인해 주세요.

EasyDrv9(万能驱动9, EDv9) 26v5의 한국어 UI를 제공하고, 드라이버 검색·매칭·설치의 핵심 기능을 유지하면서 광고성 후처리 및 불필요한 외부 연결을 줄이는 프로젝트입니다. 기능과 최종 결과물의 상세 검증 기록은 아래에 정리했습니다.

**English:** EasyDrv9 (EDv9 / 万能驱动9) v26v5 Korean localization by SoNG. Focus: Korean UI, offline driver installation workflows, removal of unwanted browser changes and clean-up residue. The [author's Korean blog post and user guide](https://blog.naver.com/shj2564/224426811365) explains the localized edition.

**검색 키워드 / Keywords:** EasyDrv9 한글판, EDv9 한국어판, 만능드라이버9 한글, EasyDrv9 26v5 Korean, 万能驱动9 韩国语, 오프라인 드라이버 설치, CLEAN OFFLINE

---

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

### FINAL ISO

- File: `EDv9_26v5_KO_CLEAN_FINAL.iso`
- SHA-256: `6AD8DC770FDDB2E27782131B6A2AB4F48C66BB66416C51AE8856EE549C96B536`
- Size: 11,951,794,176 bytes
- Filesystem: UDF 1.02
- Volume label: `EDv9_26v5_KO`
- Payload file count: 106
- Validation: PASS
- Build time: 2026-10-01 19:02:16 KST

The previous ISO hash `F660C0A32E98ECCDDBEABF744B9FB380807F8C42F34551773A19DCD1F33D8261` is obsolete and belongs to the earlier FINAL EXE.
