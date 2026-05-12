# Attenuation Auditor — DEVLOG (Archive)

V.1.0.0 ~ V.1.1.0 이력. 최신 이력은 `DEVLOG.md` 참조.

---

## V.1.1.0 — 2026-04-16

### 신규 기능

#### 1. 스캔 범위 선택기 (Scan Scope Selector)
- 옵션 패널 하단에 접을 수 있는 **스캔 범위** 패널 추가
- Actor-Mixer Hierarchy의 WorkUnit / ActorMixer / Folder / Container를 트리 구조로 표시
- WAAPI로 자식 노드 **Lazy-load** — 노드 확장 시 그 시점에 WAAPI 조회
- **멀티셀렉트** (selectmode="extended") — 범위 미선택 시 전체 스캔
- `↺` 버튼으로 트리 새로고침 (프로젝트 변경 후 반영)
- 선택 개수 레이블 실시간 업데이트 ("전체" / "N개 항목 선택됨")
- Wwise 연결 직후 자동 로드

#### 2. 예외 처리 (Exception Management)
- 결과 영역을 **Notebook** 구조로 전환: `위반 목록` + `예외 처리` 탭
- 위반 항목 선택 → **`+ 예외 처리`** 버튼으로 예외 등록
- 예외 항목은 `att_auditor_exceptions.json`에 영구 저장 (재시작 후에도 유지)
- **자동 무효화**: 재스캔 시 예외 항목의 3D 모드·Attenuation·위반 유형이 바뀌면 자동으로 위반 목록으로 복귀
- 예외 탭에서 항목 선택 → **`× 예외 해제`** 로 수동 해제
- 예외 탭 더블클릭 / "Wwise에서 보기" 버튼 — 예외 탭에서도 Wwise 오브젝트 포커스 지원

### 버그 수정 (이전 세션)

#### @OverridePositioning 계층 탐색 (`_resolve_effective`)
- **증상**: 상속된 오브젝트가 모두 "Attenuation 미설정"으로 잘못 탐지됨
- **원인**: `@OverridePositioning=false` 노드에서 WAAPI가 반환하는 포지셔닝·어테뉴에이션 값은 스테일(stale)값. 이를 그대로 읽으면 오류
- **수정**: 계층을 위로 올라가며 `@OverridePositioning=true`인 가장 가까운 조상을 찾아, 포지셔닝과 어테뉴에이션을 그 노드에서 일괄 읽음 (캐시로 중복 탐색 방지)

#### @3DSpatialization 정수 판별
- **증상**: 역방향 탐지가 정상 동작하지 않음
- **원인**: WAAPI가 문자열("Position") 대신 정수(1)를 반환. `"Position" in {0, "None", ...}` 비교 실패
- **수정**: `spat != 0` 조건으로 정수 비교

### UI 개선
- 결과 영역 Notebook 전환에 따른 탭 스타일 (`TNotebook`, `TNotebook.Tab`) 추가
- 스코프 트리 전용 스타일 (`Scope.Treeview`) 추가 — 기존 결과 트리와 행 높이·폰트 분리
- 액션 바에 예외 처리 버튼 2개 추가 (`exc` / `warn` 프리셋)
- 예외 탭 행 색상: 보라 계열 (`EXC_CLR = #BC8CFF`)
- 버전 V.1.0.0 → V.1.1.0

### 기술 노트
- 예외 키: `obj_id` (Wwise GUID). 지문(fingerprint) = `[spat_label, att_label, issue]`
- 예외 탭 Treeview iid: GUID의 중괄호가 Tcl 파싱 오류를 일으키므로 정수 인덱스 사용. `_exc_order[]` 리스트로 인덱스 → obj_id 매핑
- 스코프 토글 버블링 방지: 레이블 바인딩에서 `return "break"` 처리

---

## V.1.0.0 — 초기 배포

- 3D 오브젝트 Attenuation 미설정 탐지
- 2D 오브젝트 Attenuation 연결 역방향 탐지
- WAAPI 연결 / Watchdog / 한·영 전환
- Wwise 오브젝트 더블클릭 선택 / CSV 내보내기
- 컬럼 정렬 / 호버 강조 / 행 색상 (빨강·노랑)
