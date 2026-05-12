# Attenuation Auditor — DEVLOG

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
