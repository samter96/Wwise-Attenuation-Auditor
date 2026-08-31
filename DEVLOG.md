# Attenuation Auditor — DEVLOG

## V.2.0.0 — 2026-08-27

### Hotfix — 대형 Wwise 프로젝트 스캔 로딩 개선

- V2 백엔드가 선택한 스코프와 무관하게 Wwise 전체 프로젝트의 대상 타입을 한 번에 조회하던 문제 수정
- 스캔 쿼리를 Actor-Mixer Hierarchy 또는 선택된 scope의 descendants 기반으로 제한하고,
  OverridePositioning 상속 판정에 필요한 조상 노드만 path 배치 조회로 보강
- WAQL `where type = ...` 서버 필터링을 적용해 descendants 전체를 받은 뒤 Python에서 걸러내던 병목 제거
- 실제 WAAPI 연결 프로젝트에서 전체 스캔 응답 시간 0.012초 확인
- GitHub ZIP 다운로드에서도 최신 설치본을 받을 수 있도록 NSIS 설치 파일을 `releases/`에 포함하고 설치 문서/스크립트 경로 갱신
- 기존 3D/Attenuation 판정 계약과 예외 fingerprint는 그대로 유지

### 문서 — Wwise 애드온 툴 제품군 가이드 추가

- Stereo Auditor 디자인 시스템과 Attenuation Auditor V2 실전 구현 경험을 합쳐
  `docs/WWISE_ADDON_TOOL_DESIGN_SYSTEM.md` 작성
- Wwise/WAAPI 툴용 정보 구조, Tauri/React 앱 셸, HiDPI 선명도, 커스텀 타이틀바,
  ScopeTree/ResultsTable, Wwise command add-on, 출시 전 QA 체크리스트를 다음 툴 제작 기준으로 정리

### Hotfix — Hero 타이틀 문구 정리

- idle 상태의 메인 타이틀을 한/영 언어 설정과 무관하게 `Attenuation Auditor`로 통일

### Hotfix — 125% 이상 DPI 선명도 및 네이티브 프레임 보정

- Windows 실행 manifest에 `PerMonitorV2` DPI awareness를 명시하고, 프로세스 시작 시점에도
  동일한 DPI context를 적용해 모니터 배율 변경 시 WebView가 운영체제의 비트맵 확대 대상이 되지 않도록 수정
- WebView zoom을 100%로 고정하고 125% 모니터에서 1180×760 논리 창이 1475×950 물리 픽셀로
  렌더링되는 것을 실제 릴리스 캡처로 검증
- 작은 한국어 UI 글자는 Windows의 DPI 힌팅이 적용되는 `Malgun Gothic` 계열로 렌더링하고,
  영문은 경량 Inter Variable Latin 폰트를 내장하도록 타이포그래피 체계 정리
- borderless 창의 DWM shadow를 제거해 창 최상단에 나타나던 흰색 1px 선 제거
- 문자 `✓`에 의존하던 체크 표시를 전용 `PrecisionCheck` SVG 컴포넌트로 교체하고
  cyan gradient, inset highlight, focus/transition을 적용
- 전체 한국어 웹폰트 번들을 제거해 프런트 CSS/폰트 자산 크기와 초기 렌더링 부담 축소

### 전면 재구축 — Tauri / React 데스크톱 UI

Tkinter의 렌더링·타이포그래피·애니메이션 한계를 벗어나기 위해 UI 계층을 Tauri 2 + React로
교체했다. Stereo Auditor 디자인 시스템의 단순 색상뿐 아니라 표면 계층, 밀도, 서체,
hairline, 상태 전환과 모션 문법까지 동일한 제품군 언어로 재구성했다.

#### 비주얼 / UX

- Inter Variable Latin 폰트를 내장하고 한국어는 Windows DPI 힌팅 폰트 스택을 사용
- 커스텀 타이틀바, 프로젝트 연결 바, hero, 컨트롤 스트립, 3열 메트릭, 범위/결과 패널 구현
- 스캔 상태에 반응하는 SVG Attenuation 궤도와 파형, glow, scan line 애니메이션 구현
- 위반/예외 탭, 다중 범위·결과 선택, Wwise 이동, CSV, 예외 등록/해제, KO/EN, 도움말 제공
- 1180×760 기본 창 및 860×600 최소 창, 축소 폭 responsive 레이아웃과 reduced-motion 대응
- 위반 비율이 매우 낮을 때 점수가 100으로 오인되지 않도록 99점대는 소수 1자리로 표시

#### 백엔드 / 패키징

- `auditor_core.py`로 판정 계약을 UI에서 분리하고 `auditor_backend.py` JSON-lines sidecar 추가
- Rust 프로세스 브리지가 persistent Python 백엔드를 관리하며 transport 장애에만 1회 재시작
- PyInstaller 단일 백엔드 실행파일을 Tauri resource로 포함
- 설치본의 예외 데이터와 백엔드 작업 폴더는 사용자별 Windows 앱 데이터 경로를 사용
- 기존 프로젝트 폴더의 `att_auditor_exceptions.json`은 V2 최초 실행/설치 시 자동 마이그레이션
- Windows x64 NSIS 설치 프로그램 및 소스용 `build_v2.bat` 생성
- `launch.bat` / Wwise command add-on이 설치본과 로컬 릴리스 빌드를 우선 사용하도록 변경

#### 판정 계약 보존

- 3D 판정은 `ListenerRelativeRouting=on AND 3DSpatialization in {1, 2}`를 그대로 유지
- `EnableAttenuation=on AND Attenuation.name 존재` 조건, null GUID 처리, 최근접 Override 상속 유지
- `miss = 3D AND NOT ATT`, `extra = 2D AND ATT` 양방향 검사를 그대로 유지
- WorkUnit / PhysicalFolder `filePath` 구분과 예외 fingerprint 자동 무효화 유지

#### 검증

- Python core/backend 자동 테스트 9개 통과
- `npm run build`, `cargo check`, `npm run tauri -- build` 통과
- PyInstaller 백엔드의 `ping` JSON 응답과 버전 `V.2.0.0` 확인
- 릴리스 앱에서 포함된 `auditor_backend.exe` 자식 프로세스 기동 확인
- 1180×760 브라우저 및 실제 Tauri 릴리스 창에서 idle/scanning/result 상태 시각 검수
- 산출물: `src-tauri/target/release/attenuation-auditor.exe`
  및 `src-tauri/target/release/bundle/nsis/Attenuation Auditor_2.0.0_x64-setup.exe`

---

## V.1.5.0 — 2026-08-26

### UI — Stereo Auditor 제품군 디자인 시스템 적용

`STEREO_AUDITOR_DESIGN_SYSTEM.md`의 시각 언어를 Tkinter 환경에 맞게 이식했다.
판정 로직과 WAAPI 데이터 계약은 변경하지 않았다.

#### 디자인 토큰

- 배경/기본 표면/상승 표면을 `#090b0f` / `#0d1015` / `#11151c`로 분리
- 브랜드 계층은 cyan → blue → violet, 검토 상태는 amber로 통일
- `miss` 빨강 / `extra` 노랑 판정색과 라벨을 함께 유지
- 주·보조·약한 텍스트 대비를 제품군 토큰에 맞게 상향
- 버튼 hover/press/focus hairline과 키보드 focus 표시 추가

#### 레이아웃과 컴포넌트

- Attenuation 거리 곡선을 추상화한 3색 브랜드 마크와 1px 컬러 레일 추가
- 감사 설정을 독립된 raised card로 구성하고 판정 범례를 행동 가까이에 배치
- 검사 오브젝트 / 위반 / 예외의 3열 메트릭 스트립 추가
- 범위 트리와 결과 탭을 hairline panel로 분리하고 표 행 높이·헤더·탭 대비 개선
- 하단 액션을 좌측 일반 행동 / 우측 예외 행동으로 정리
- 기본 창 1180×760, 중앙 배치, 최소 창 860×600으로 조정
- 최소 창에서도 결과 트리가 하단 액션 바를 밀어내지 않도록 pack 순서 보정
- 한국어/영어에 설정 설명, 메트릭, 범례 문자열 추가

#### 검증

- 4개 Python 모듈 `py_compile` 통과
- 1180×760 실제 Tk 렌더 캡처로 시각 검수
- 860×600에서 KO/EN 모두 스캔·내보내기·예외 버튼과 결과 트리 노출 확인
- 핵심 판정식 `bool(lr) and spat in {1, 2}`, `att_active`, `miss/extra` 분기 무변경 확인

---

## V.1.4.0 — 2026-05-12

### UX — 스캔 항목 토글 제거, 두 위반 항상 함께 검사

기존 옵션 패널의 `miss` / `extra` 체크박스를 제거. 결과 목록의 `Issue` 컬럼만으로
위반 종류를 충분히 구분할 수 있으므로, 토글로 한쪽을 끄는 워크플로는 불필요했음.

#### 코드 변화

- 제거: `_opt_miss_att`, `_opt_extra_att` (BooleanVar), `_chk_miss`, `_chk_extra`,
  `_lbl_scan_opts` 위젯, 옵션 패널 좌측 `grp1` 프레임 전체
- `_run_scan`: 옵션 미선택 가드(`no_opt`) 제거, `check_miss`/`check_extra` 분기 제거,
  `is_3d → miss` / `not is_3d AND att_active → extra` 로 단순화
- `_refresh_lang`: 해당 위젯 라벨 갱신 라인 제거

#### 부수 정리

- `auditor_strings.py`: `_TIP_MISS_KO/EN`, `_TIP_EXTRA_KO/EN` 본문 + `_S` 내 키
  (`no_opt`, `opt_miss_att`, `opt_extra_att`, `scan_opts_hdr`, `tip_miss`, `tip_extra`) 일괄 제거
- `auditor_ui_helpers.py`: 더 이상 호출자가 없는 `_make_tip_btn` 제거
- `attenuation_auditor.py`: `from auditor_ui_helpers import _make_tip_btn, _ab` →
  `_ab` 만 import
- 도움말 본문: 「스캔 항목」 섹션을 「스캔」 섹션으로 통합. miss/extra 가 각각 무엇인지
  짧게 명시

#### 검증

- 4 개 파일 `py_compile` 통과
- `import attenuation_auditor` 성공, `VERSION = "V.1.4.0"` 확인

### 문서

- `README.md`: 4 항목 (LRR / Spat / AttEn / AttSet) 의 16 경우의 수 매트릭스 추가
  + 핵심 2×2 매트릭스 추가. "기여 / 문의" / 라이선스 placeholder 정리

### Hotfix — `install.bat` pip 업그레이드 호출 방식

pip 26.x 부터 Windows 에서 `pip.exe install --upgrade pip` 직접 호출이 거부됨
(자기 자신 덮어쓰기 불가). `python.exe -m pip` 형태로 변경.

- `.venv\Scripts\pip install --upgrade pip --quiet`
  → `.venv\Scripts\python.exe -m pip install --upgrade pip --quiet`
- waapi-client 설치 호출도 동일 형태로 통일

---

## V.1.3.0 — 2026-05-06

### 리팩터링 — 모듈 분리 (토큰 효율 + 유지보수성)

기존 `attenuation_auditor.py` 1527 줄 단일 파일을 4 개로 분리:

| 파일 | 내용 | 줄수 |
|------|------|------|
| `attenuation_auditor.py` | `AttenuationAuditor` 클래스 (UI + 스캔 + WAAPI) | ~1190 |
| `auditor_constants.py`   | VERSION, 색상, 폰트, 타입 상수, 아이콘 맵 | ~75 |
| `auditor_strings.py`     | `_S` 한·영 사전, `_TIP_*` 툴팁 본문 | ~205 |
| `auditor_ui_helpers.py`  | `_ab` (animated button), `_make_tip_btn` | ~55 |

### 문서 트림
- 프로젝트 컨텍스트 문서: 버그 이력 표 / 설치·배포 / 코드 스니펫 제거 → 핵심 판정 규칙 + WAAPI 노트만 유지.
- `DEVLOG.md`: V.1.0.0 ~ V.1.1.0 항목을 `DEVLOG_archive.md` 로 분리.

### 검증
- 4 개 파일 모두 `py_compile` 통과
- `import attenuation_auditor` 성공, `VERSION = "V.1.3.0"` 확인
- 외부 진입점(`launch.bat`, `install_addon.bat`) 변경 없음 (메인 파일 이름 그대로 유지)

---

## V.1.2.4 — 2026-05-06

### 핫픽스 — `is_3d` 판정에 `3DSpatialization` 다시 포함 (V.1.2.0 회귀 정정)

**증상**: `LRR=on` 이지만 `3DSpatialization=None(0)` 인 의도된 2D 사운드가 `miss` 위반으로 잡힘. 사용자 보고 자산: `AMB_3D_Spline_Water_River_WM_Set_A_SFX` (BlendContainer).

**진짜 원인**: 보고된 자산은 `OP=false` 상속 객체. effective 노드는 부모 `AMB_3D_Volume` (ActorMixer).

```
AMB_3D_Volume:
  @OverridePositioning = true
  @ListenerRelativeRouting = true       ← LR 켜져 있긴 함
  @3DSpatialization = 0                  ← None! 거리 감쇠 미적용
  @EnableAttenuation = true
  @Attenuation = {"id": "{00000000-...}"}  ← null GUID, name 없음
```

`3DSpatialization=None` 이면 LR 이 켜져 있어도 게임에서 거리 감쇠가 적용되지 않음. 즉 의도된 2D 사운드. V.1.2.0 에서 `is_3d = bool(lr)` 단독 판별로 바꾼 게 이 케이스를 잘못 3D 로 간주한 회귀였음.

**수정**: `is_3d = bool(lr) and spat != 0` 로 환원 (V.1.1.0 기준).

### V.1.2.0 DEVLOG 의 "3D 판정 기준 변경" 항목은 잘못된 기재였음

V.1.2.0 항목 "3D 판정 기준 변경: bool(lr) and spat != 0 → bool(@ListenerRelativeRouting) 단독" 은 사용자 의도에 부합하지 않음. V.1.2.4 에서 V.1.1.0 기준으로 되돌림.

### 새 데이터 포인트 — null GUID Attenuation

WAAPI 가 `@Attenuation` 을 `{"id": "{00000000-0000-0000-0000-000000000000}"}` 로 반환하는 케이스 확인됨 — Wwise UI 에서 ShareSet 미연결 상태에 해당. 이때 응답에 `name` 필드가 없으므로 `att_ref.get("name", "")` 가 빈 문자열을 반환하여 자동 처리됨. 별도 GUID 검사 불필요.

---

## V.1.2.3 — 2026-05-06

### 핫픽스 — `extra` 판정 오탐 수정 (V.1.2.1 회귀)

**증상**: 의도된 2D 사운드(`CR_PC_Skill_Impact_Rock_WS_P1` 등)가 `extra` 위반으로 잡힘.

**원인**: V.1.2.1에서 DEVLOG V.1.2.0 의 "extra: LR=off AND ATT name 설정 (enable 여부 무관)" 기재를 그대로 따라 `att_linked = bool(att_name)` 변수를 도입했음. 그러나 실제 툴팁(`_TIP_EXTRA_KO/EN`)은 일관되게 "Attenuation Enable = 활성화 + ShareSet 설정됨" 으로 두 조건을 모두 요구하고 있었고, 이쪽이 사용자 의도에 부합. `Enable=off` 상태에서는 게임 런타임에 어테뉴에이션이 전혀 적용되지 않으므로 2D 의도로 봐야 함.

**수정**:
- `att_linked` 변수 제거. `extra` 판정도 `att_active` (Enable + ShareSet 둘 다)를 사용하도록 환원.
- 프로젝트 컨텍스트 문서의 위반 유형 표를 "실효 어테뉴에이션" 개념으로 다시 작성.

### 코드 변화

```python
# Before (V.1.2.1)
att_active = bool(att_enable) and bool(att_name)
att_linked = bool(att_name)
...
elif check_extra and not is_3d and att_linked: issue = "extra"

# After (V.1.2.3)
att_active = bool(att_enable) and bool(att_name)
...
elif check_extra and not is_3d and att_active: issue = "extra"
```

---

## V.1.2.2 — 2026-05-06

### 개선 — 스코프 트리 가상 루트 추가

기존: 트리 최상단에 워크유닛 / 피지컬폴더가 직접 나열되어, "전체 스캔"을 명시적으로 지정할 수 없었음 (선택 해제로만 가능).

수정:
- 트리 최상단에 가상 루트 노드 `전체 (Actor-Mixer Hierarchy)` 추가
- 루트 path = `\Actor-Mixer Hierarchy` — 기존 `_matches_scope` 의 prefix 매칭으로 모든 자식이 자동 포함
- 기본 expand 상태로 표시
- `_get_scope_paths()`: 루트만 선택 시 빈 집합으로 정규화 → 매 객체별 startswith 검사 생략
- `_update_scope_label()`: 루트만 선택돼도 "전체"로 표시 (UX 일관성)

---

## V.1.2.1 — 2026-05-06

### 핫픽스 — V.1.2.0 판정 로직 코드 반영

V.1.2.0 DEVLOG에 명시된 판정 기준이 실제 코드에 누락되어 있던 것을 정정.

#### 1. `is_3d` 판정 — `@ListenerRelativeRouting` 단독 적용
- 기존 코드: `is_3d = bool(lr) and spat != 0` (V.1.1.0 잔재)
- 수정: `is_3d = bool(lr)` — DEVLOG 기재 사항과 일치

#### 2. `extra` 판정 — `enable` 무관, ShareSet 참조 유무로 판단
- 기존 코드: `extra` 분기에 `att_active = (att_enable AND att_name)` 사용 → enable 꺼져 있으면 탐지 누락
- 수정: `att_linked = bool(att_name)` 신규 변수 도입, extra 분기에서 사용
- miss 분기는 그대로 `att_active` (enable + ShareSet 둘 다 필요)

#### 3. `eff is None` 처리 — `continue` 로 변경
- 기존 코드: 조상에 override 없으면 자기 자신(`obj`)을 fallback으로 사용 → V.1.0.0 시기 stale 값 오탐 경로 재진입
- 수정: 기본 2D / no-ATT 로 간주하고 스킵

#### 4. 디버그 코드 제거
- `scan_debug.txt` 파일 작성 로직 (`_DBG_TARGETS`, `_dbg_file` 등) 일괄 제거
- 사용자 환경에서도 매 스캔마다 파일이 생기던 문제 해결

### 검토만 한 사항 (변경 없음)

#### `_resolve_effective` 의 "OP 키 없음 + LR 키 있음 → override" 추론
- 의도: WAAPI 응답에서 `@OverridePositioning` 키가 누락되는 경우의 방어적 fallback
- 현재 동작: 정상 시 WAAPI는 포지셔닝 가능 타입에 대해 항상 키를 반환하므로 이 분기는 거의 타지 않을 것으로 추정
- 변경하지 않은 이유: 실측 없이 변경하면 WAAPI가 키를 누락하는 엣지 케이스에서 회귀 가능성. 별도 검증 후 결정

---

## V.1.2.0 — 2026-04-16

### 버그 수정 (추가)

#### PhysicalFolder 아이콘 구분
- **증상**: 스코프 트리에서 WorkUnit과 PhysicalFolder가 동일한 아이콘으로 표시됨
- **원인**: WAAPI가 두 타입 모두 `type: "WorkUnit"`으로 반환
- **수정**: `_effective_type()` 메서드로 재분류 — `filePath`가 `.wwu`로 끝나지 않으면 `"PhysicalFolder"`로 처리. `_ICON_MAP`에 `ObjectIcons_PhysicalFolder_nor.png` 추가

#### 스캔 판정 기준 전면 재정의
- **3D 판정 기준 변경**: 기존 `bool(lr) and spat != 0` → **`bool(@ListenerRelativeRouting)` 단독**
  - `@3DSpatialization`은 컬럼 표시용으로만 유지, 판정에서 제외
- **miss 판정**: `LR=on` AND NOT (`ATT enable=on` AND `ATT name 설정`) → 3D인데 ATT 미설정
- **extra 판정**: `LR=off` AND `ATT name 설정` (enable 여부 무관) → 2D인데 ATT 참조 존재
- `eff is None` → `continue` (조상 override 없으면 기본 2D/no-ATT로 간주, 스킵)

### 신규 기능

#### 1. 스캔 범위 → 좌측 세로 패널로 재배치
- `tk.PanedWindow(orient="horizontal")` 로 좌(스코프) + 우(결과 Notebook) 분리
- 사용자가 sash 드래그로 좌우 패널 너비 조절 가능 (minsize 140 / 400)
- Wwise 설치 폴더에서 오브젝트 타입 아이콘 자동 로드: `_load_type_icons()`
  - 경로: `C:\Audiokinetic\*\Authoring\Data\Themes\classic\images\ObjectIcons`
  - `ObjectIcons_ActorMixer_nor.png` 등 Bus Routing Auditor와 동일한 매핑
  - 아이콘 로드 실패 시 유니코드 폴백 문자로 자동 대체

#### 2. 컬럼 드래그 재배치
- 헤더를 8px 이상 드래그하면 컬럼 순서 변경 (`displaycolumns` 갱신)
- 헤더 클릭(드래그 없음)은 기존 정렬 유지
- `_col_dragging` 플래그: 드래그 직후 heading command(sort) 억제
- 위반 목록 / 예외 처리 탭 두 트리뷰 모두 동일한 `_col_order` 공유

#### 3. 다중 선택 (Multi-select)
- `selectmode="extended"` — 위반 목록 · 예외 처리 탭 모두
- `+ 예외 처리`: 선택된 모든 위반 항목 일괄 예외 등록
- `× 예외 해제`: 선택된 모든 예외 항목 일괄 해제

#### 4. 스캔 옵션 툴팁
- 각 체크박스 호버 시 500ms 딜레이 후 툴팁 표시
- 판단 기준 (`_TIP_MISS_KO/EN`, `_TIP_EXTRA_KO/EN`) 한·영 전환 연동
- `_Tooltip` 모듈 레벨 클래스: `<Enter>/<Leave>/<ButtonPress>` 바인딩

---

V.1.0.0 ~ V.1.1.0 이력은 `DEVLOG_archive.md` 참조.
