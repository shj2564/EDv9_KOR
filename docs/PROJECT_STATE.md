# PROJECT STATE

Last updated: 2026-09-29 KST

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

2026-09-29 기준 공개 배포 흔적이 확인된 다음 세대.

현재 저장소 기준 상태:
- 원본 전체 패키지: 미등록
- 정확한 내부 9.0.x 빌드번호: 원본 확보 후 검증
- 원본 EXE/DAT SHA-256: 원본 확보 후 검증
- 26v4 대비 binary/token/XQS diff: 대기

### 26v5 작업 순서

1. 원본 ZIP/S7Z 확보
2. 전체 패키지 SHA-256
3. EXE/DAT/INI/@version 안전 추출
4. EXE/DAT SHA-256
5. PE / AutoIt EA06 / SCRIPT offset 확인
6. XQS 구조 확인
7. 26v4 함수/문자열/token diff
8. DAT 바인딩 구조 확인
9. SoftInst / wget / inst.cmd / inst.vbs 확인
10. Edge/브라우저 조작 코드 확인
11. ITSK/123/2345/360 관련 네트워크 경로 확인
12. UnmountDrv 정상 경로 분리 확인
13. 기존 한국어 UI 이식
14. 신규 문자열 번역 및 길이 조정
15. CLEAN OFFLINE neutralization
16. 바인딩 검증
17. No-Residue 패처
18. Windows 실사용 테스트
19. 배포 기준 SHA-256 확정

## Repository policy

- 메뉴 자체는 임의 삭제하지 않는다.
- UI 잘림은 자연스러운 축약으로 처리한다.
- 드라이버 핵심 기능은 보존한다.
- CLEAN 대상은 단순 UI 숨김보다 실행 경로 제거/무력화를 우선한다.
- 원본 복원 가능성을 유지한다.
- 패치 배포 파일 수는 최소화한다.
- 임시/백업 찌꺼기는 종료 후 제거한다.
- 대용량 원본 패키지 및 드라이버 DB/WIM은 Git 히스토리에 직접 넣지 않는다.
