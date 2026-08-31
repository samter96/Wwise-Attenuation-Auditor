# Attenuation Auditor — 프로젝트 컨텍스트

Wwise WAAPI 를 통해 Actor-Mixer Hierarchy 를 스캔, Attenuation 위반을 탐지하는 Python/Tkinter GUI.

- **버전**: V.1.4.0
- **언어**: 한국어로 대화

## 파일 구조

```
attenuation_auditor.py    # AttenuationAuditor 클래스 (UI + 스캔 + WAAPI 연결)
auditor_constants.py      # VERSION, 색상, 폰트, 타입 상수, 아이콘 맵
auditor_strings.py        # _S 한·영 사전
auditor_ui_helpers.py     # _ab (animated button)
DEVLOG.md                 # 최근 변경 이력 (V.1.2.x ~)
DEVLOG_archive.md         # V.1.0.0 ~ V.1.1.0
README.md                 # GitHub 사용자용 문서 (판정 매트릭스 포함)
att_auditor_exceptions.json  # 자동 생성
.venv/
launch.bat / install.bat / install_addon.bat
```

## 위반 판정 규칙 (V.1.2.4 기준, 변경 금지)

V.1.4.0 부터 UI 의 miss/extra 토글이 제거되어 **두 위반을 항상 함께 검사**.
판정 로직 자체는 동일.


`_resolve_effective(path)` 가 OverridePositioning=true 인 가장 가까운 조상 노드를 찾아 그 값을 effective 로 사용. 못 찾으면 skip (기본 2D / no-ATT 로 간주).

- **3D 사운드** = `LR=on` AND `3DSpatialization in {1, 2}`
  - spat=None(0) 이면 LR 켜져있어도 거리 감쇠 미적용 → 의도된 2D
- **실효 어테뉴에이션** = `EnableAttenuation=on` AND `Attenuation.name 설정`
  - null GUID `{00000000-...}` 는 `name` 필드 없음 → 미연결로 자동 처리

| 유형 | 조건 | 색 |
|------|------|----|
| `miss`  | 3D AND NOT 실효 ATT | 빨강 |
| `extra` | 2D AND 실효 ATT     | 노랑 |

**금지 변경** (회귀 두 번 발생): `is_3d = bool(lr)` 단독으로 단순화하지 말 것. spat 검사 필수. 자세한 이유는 메모리 `feedback_attenuation_3d_rule.md` 참조.

## WAAPI 노트
- `@3DSpatialization`: 정수 (0=None, 1=Position, 2=Position+Orientation)
- `@OverridePositioning`: True / False / 키 없음 (Folder·WorkUnit 은 키 자체 없음)
- WorkUnit / PhysicalFolder 모두 `type="WorkUnit"` 으로 반환 → `filePath` 가 `.wwu` 로 끝나지 않으면 PhysicalFolder
- `@Attenuation` 이 ShareSet 미연결이면 `{"id":"{00000000-...}"}` 로 반환되며 `name` 필드 없음

## 개발 규칙
- 작업 완료 시 `DEVLOG.md` 항상 업데이트
- 버전 상수: `auditor_constants.VERSION`
- 토큰 효율: 작업 영역만 명시해서 부분 read 가능하게 — "스캔 로직 X 함수의 Y 부분"
