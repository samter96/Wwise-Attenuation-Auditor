# Wwise Add-on Tool Design System

> 문서 버전: 1.0  
> 기준 앱: Stereo Auditor V1.0.0, Attenuation Auditor V2.0.0  
> 작성일: 2026-08-27  
> 목적: Wwise WAAPI 기반 애드온/데스크톱 툴을 같은 제품군 품질로 빠르게 설계, 구현, 검수한다.

---

## 0. 사용법

이 문서는 단순 색상표가 아니다. 다음 Wwise 애드온 툴을 만들 때 `문제 정의 -> 데이터 계약 -> 화면 구조 -> 컴포넌트 -> 패키징 -> QA` 순서로 확인한다.

- Stereo Auditor 문서는 제품군의 시각 언어와 계측기 감각의 원본이다.
- Attenuation Auditor V2는 Wwise/WAAPI 스캐너형 툴에 맞춘 실제 적용본이다.
- 새 툴은 색만 복사하지 말고, 정보 계층과 검증 루틴까지 함께 복사한다.

문서의 규칙은 세 종류로 구분한다.

| 표기 | 의미 |
|---|---|
| [FAMILY] | Stereo Auditor에서 확정된 제품군 공통 규칙 |
| [WWISE] | Wwise WAAPI 애드온 툴에서 추가된 규칙 |
| [STD] | Windows, Tauri, WebView, 접근성, HiDPI 기술 규칙 |

---

## 1. 디자인 DNA

### 한 문장 정의

정밀한 오디오 계측기의 신뢰도와 Wwise 제작 툴의 실무 밀도를, 어둡고 선명한 작업면 위에 작은 데이터와 즉시 실행 가능한 액션으로 표현한다.

### 고정 원칙

1. 데이터가 주인공이다. 장식은 상태, 범위, 위반 위치, 다음 행동을 더 빨리 읽게 할 때만 쓴다.
2. 어두움은 검정이 아니라 깊이의 체계다. 배경, 표면, 상승 표면을 미세하게 나눈다.
3. 색은 의미다. cyan/blue/violet은 제품군과 활성 데이터, amber는 검토, red는 위반/실패다.
4. Wwise 툴은 반복 사용 도구다. 랜딩 페이지처럼 크고 느슨하게 만들지 않는다.
5. 작은 UI도 고해상도여야 한다. 체크마크, 로고, 상태 그래픽은 텍스트 기호나 저해상도 PNG 확대에 의존하지 않는다.
6. 모션은 고급스러운 장식이 아니라 상태의 언어다. 연결 중, 스캔 중, 결과 도착, 선택 전환을 설명한다.
7. 한/영 전환은 DOM 구조를 바꾸지 않는다. 같은 레이아웃에서 문자열만 바뀌어야 한다.

### 피해야 할 인상

`색만 칠한 스킨`, `흐릿한 125% DPI`, `네온 게임 UI`, `과한 카드`, `거친 체크 표시`, `표만 던진 내부 툴`, `복제한 듯한 외부 제품 UI`

---

## 2. Wwise 애드온 툴의 기본 정보 구조

WAAPI 기반 감사/정리/검출 툴은 대부분 아래 구조를 따른다.

```text
Launch
  -> Connect to Wwise
  -> Load project context
  -> Choose scope / object types / options
  -> Run scan or operation
  -> Review result table
  -> Select rows
  -> Jump to Wwise / export / exception / fix action
```

화면은 한 장 안에서 다음 순서로 읽히게 만든다.

1. 현재 Wwise 연결 상태와 프로젝트
2. 이 툴이 찾는 문제 또는 수행하는 작업
3. 스캔 범위와 옵션
4. 핵심 점수/개수/상태
5. 결과 테이블
6. Wwise로 돌아가는 행동

파일 분석형 Stereo Auditor와 달리, Wwise 애드온 툴의 주 작업면은 `트리 + 결과 테이블`이다. 시각화는 파형이 아니라 스캔 상태, 위반 밀도, 구조적 범위를 설명하는 보조 장치가 된다.

---

## 3. 추천 기술 스택

### 데스크톱 셸

- Tauri 2 + React + TypeScript를 기준으로 한다.
- Tkinter는 빠른 내부 프로토타입에는 가능하지만, 고해상도 타이포그래피, 부드러운 모션, 커스텀 타이틀바, HiDPI 검수 품질을 맞추기 어렵다.
- UI와 Wwise 로직은 분리한다. React는 상태와 표시, Python/Rust/backend는 WAAPI 계약과 파일 작업을 맡는다.

### 패키지 기준

```json
{
  "dependencies": {
    "@fontsource-variable/inter": "...",
    "@tauri-apps/api": "...",
    "@tauri-apps/plugin-dialog": "...",
    "lucide-react": "...",
    "react": "...",
    "react-dom": "..."
  }
}
```

아이콘은 `lucide-react`를 기본으로 한다. 직접 그리는 SVG는 브랜드 마크, 상태 오비트, 정밀 체크처럼 제품 고유 그래픽일 때만 사용한다.

---

## 4. 디자인 토큰

### 색상

```css
:root {
  --bg: #090b0f;
  --surface: #0d1015;
  --raised: #11151c;
  --line: rgba(255, 255, 255, 0.075);
  --line-soft: rgba(255, 255, 255, 0.045);
  --text: #edf1f8;
  --muted: #a1aabc;
  --faint: #778195;
  --cyan: #55d5ef;
  --blue: #6a86ff;
  --violet: #a869ff;
  --amber: #eeb34f;
  --danger: #f06468;
}
```

역할별 규칙:

| 역할 | 색 |
|---|---|
| 앱 배경 | `--bg` |
| 기본 패널 | `--surface`, `--raised` |
| 보더/hairline | `--line`, `--line-soft` |
| 주 텍스트 | `--text` |
| 보조 텍스트 | `--muted` |
| 비활성/메타 | `--faint` |
| 연결됨/정상/활성 | `--cyan` |
| 선택/제품군 강조 | `--blue`, `--violet` |
| 의도적 예외/주의/검토 | `--amber` |
| 위반/실패 | `--danger` |

red는 실패나 실제 위반에만 쓴다. 강조가 필요하다고 red를 쓰면 위반 의미가 흐려진다.

### 타이포그래피

```css
:root {
  font-family:
    "Inter Variable", Inter,
    "Pretendard Variable", Pretendard,
    "Noto Sans KR", "Malgun Gothic",
    "Segoe UI Variable", "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
}
```

이번 Attenuation Auditor에서 확인한 실전 규칙:

- 영문은 Inter Variable을 내장한다.
- 한국어는 Windows DPI 힌팅이 좋은 `Malgun Gothic` 계열 fallback을 반드시 확인한다.
- 한글 전체 웹폰트를 무겁게 번들링하면 초기 렌더링과 선명도 검수에 손해가 날 수 있다.
- 숫자는 `font-variant-numeric: tabular-nums`를 쓴다.
- 영어 대문자 label에는 `.09em` 안팎 tracking을 쓸 수 있지만, 한국어에 그대로 적용하지 않는다.
- 앱 전체에서 viewport 기준 폰트 스케일링을 하지 않는다. 작은 툴 UI는 예측 가능한 픽셀 크기가 중요하다.

권장 크기:

| 스타일 | 크기 | 굵기 | 용도 |
|---|---:|---:|---|
| Product title | 11px | 600 | 타이틀바 |
| Hero title | 25-36px | 480 | 현재 작업/결과 제목 |
| Metric value | 22-32px | 470 | 점수, 위반 수 |
| Panel heading | 10px | 570 | 패널 제목 |
| Table body | 8.5-9px | 500-550 | 결과 행 |
| Label | 7.5-9px | 650-700 | uppercase label |
| Tiny meta | 7-8px | 600 | 버전, 경로, 보조 설명 |

---

## 5. 앱 셸과 레이아웃

### 기본 창

| 항목 | 기준 |
|---|---|
| 기본 크기 | 1180 x 760 |
| 최소 크기 | 860 x 600 |
| titlebar | 38px custom chrome |
| project bar | 42-48px |
| hero | 112-160px |
| control strip | 54-60px |
| metrics strip | 58-74px |
| workspace | scope tree + result table |

Wwise 툴의 기본 레이아웃:

```text
WindowChrome
ProjectBar
Hero: purpose/result + state graphic + score
ControlStrip: scope/object options + legend + primary action
MetricsStrip: checked / violations / exceptions
Workspace: ScopeTree | ResultsTable
```

### 창 표면

```css
.app-shell {
  background:
    radial-gradient(circle at 59% 28%, rgba(63, 82, 133, .078), transparent 30%),
    linear-gradient(145deg, #0b0e13 0%, var(--bg) 46%, #080a0d 100%);
}

.app-shell::before {
  background-image: linear-gradient(rgba(255,255,255,.012) 1px, transparent 1px);
  background-size: 100% 80px;
}
```

배경 그리드는 거의 보이지 않아야 한다. 축소 스크린샷에서 줄무늬가 먼저 보이면 실패다.

### 패널

```css
.panel {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(17,21,28,.88), rgba(11,14,19,.82));
  box-shadow: inset 0 1px rgba(255,255,255,.018), 0 18px 45px rgba(0,0,0,.12);
}
```

Wwise 작업툴에서는 과한 card 중첩을 피한다. 큰 화면 구획은 panel, 반복 데이터는 table row, 예외/상태는 badge로 처리한다.

---

## 6. 필수 컴포넌트

### WindowChrome

- 높이 38px.
- `decorations: false`를 쓰고 React에서 custom chrome을 만든다.
- 빈 영역, 로고, 제품명, 버전에는 `data-tauri-drag-region`을 둔다.
- 버튼 위에서는 drag가 시작되면 안 된다.
- Help, Reconnect, KO/EN toggle, minimize/maximize/close를 오른쪽에 둔다.
- close hover만 red 배경을 허용한다.

### ProjectBar

Wwise 툴은 현재 연결과 프로젝트 맥락이 첫 번째 신뢰 신호다.

구성:

- connection badge: connecting / connected / error
- project name
- hierarchy or active root
- `WAAPI · LOCAL PROCESSING` 같은 처리 위치 표시

상태 색:

| 상태 | 색 |
|---|---|
| connected | cyan |
| connecting | amber pulse |
| error/disconnected | danger |

### Hero

Hero는 마케팅 문구가 아니라 현재 작업 상태다.

Idle:

- title: 제품명 또는 툴의 짧은 목적
- body: 무엇을 어떤 기준으로 검사하는지 한 문장
- criteria/help button

Scanning:

- title: 현재 분석 중임을 명확히 표시
- body: 어떤 기준을 해석 중인지 설명
- 가짜 진행률은 금지

Complete:

- issue count가 있으면 문제 수를 크게 표시
- clean이면 정상 문구와 cyan 계열 상태
- 결과 선택 후 Wwise로 이동할 수 있음을 안내

### State Graphic

Stereo Auditor의 waveform처럼 Wwise 툴에는 상태 오비트가 중심 그래픽 역할을 한다.

규칙:

- 160-180px 내외.
- cyan -> blue -> violet gradient.
- dashed orbit은 scanning 상태에서만 천천히 회전.
- 결과 도착 시 500-700ms settle animation.
- 위반이 있으면 중앙 count, 없으면 전용 vector check.
- 의미 없는 장식용 orb나 bokeh는 쓰지 않는다.

### Precision Check

체크마크는 텍스트 `✓`를 쓰지 않는다. 반드시 SVG path로 만든다.

```tsx
<svg viewBox="0 0 12 12" aria-hidden="true">
  <path d="M3 6.2l2 2L9.2 3.8" />
</svg>
```

CSS:

- check box 15-16px.
- radius 5px.
- checked background: cyan gradient.
- inset highlight와 약한 glow.
- hover/focus/active transition 120-160ms.

### Control Strip

구성:

- object type toggles
- issue legend
- primary scan/run button

규칙:

- primary action은 오른쪽 끝에 둔다.
- label과 icon은 31-36px 높이 안에서 정확히 중앙 정렬한다.
- 작은 toggle도 focus-visible이 있어야 한다.
- disabled 상태는 opacity만 낮추지 말고 cursor와 색도 안정적으로 보인다.

### Scope Tree

Wwise 계층 탐색은 왼쪽 패널에 둔다.

- 폭 220-250px.
- root/all 선택을 항상 제공한다.
- expander, object icon, label, checkbox를 한 행에 둔다.
- 선택 행은 blue inset line과 낮은 alpha background.
- 이름은 ellipsis, 전체 경로는 tooltip/title 또는 별도 상세 영역에서 제공한다.
- lazy load를 지원한다.

### Results Table

오른쪽 주 작업면이다.

- sticky header.
- row height 40-44px.
- 첫 컬럼은 name + path 2줄 구조.
- issue는 pill badge와 색 점을 함께 사용한다.
- double click은 Wwise select/jump 같은 직접 행동으로 연결한다.
- 하단 footer에는 `View in Wwise`, `Export`, `Exception/Fix` 같은 후속 행동을 둔다.

표 컬럼은 도구마다 바꾸되, 의미 순서는 유지한다.

```text
Object Name | Type | Domain-specific State A | Domain-specific State B | Issue | Work Unit
```

### Criteria Modal

판정 기준은 숨기면 안 된다.

- 현재 툴의 검사 계약을 수식/조건으로 명시한다.
- 가능한 위반 유형을 전부 보여준다.
- 사용자에게 "왜 이게 걸렸는지" 설명할 근거가 되어야 한다.
- 분석 정책을 바꾸면 modal, tests, docs를 함께 바꾼다.

---

## 7. 모션 시스템

### 시간 토큰

| 용도 | 시간 |
|---|---:|
| tiny hover | 120-140ms |
| control transition | 140-180ms |
| view enter | 420ms |
| modal/toast enter | 160-260ms |
| result settle | 500-700ms |
| scanning orbit | 5-12s 반복 |

Easing:

```css
cubic-bezier(.16, 1, .3, 1)
```

### 규칙

- scanning처럼 실제 작업 중인 상태에서만 반복 motion을 적극 사용한다.
- hover는 1px translate 또는 미세 brightness 정도로 끝낸다.
- table row hover에 큰 이동이나 scale을 주지 않는다.
- reduced motion을 지원한다.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
```

---

## 8. Wwise/WAAPI 데이터 계약

Wwise 툴은 UI보다 판정 계약이 먼저다. UI는 계약을 예쁘게 보여주는 계층이지, 계약을 즉석에서 바꾸면 안 된다.

### Backend boundary

권장 구조:

```text
React UI
  -> Tauri command
  -> Rust bridge
  -> persistent Python backend
  -> WAAPI
```

장점:

- UI freeze를 줄인다.
- WAAPI/scan 로직을 Python 테스트로 검증하기 쉽다.
- 패키징 시 backend 실행파일을 Tauri resource로 넣을 수 있다.

### Command protocol

JSON-lines request/response 구조를 권장한다.

```json
{"id":1,"command":"scan","payload":{"scopePaths":[]}}
{"id":1,"ok":true,"data":{"results":[]}}
```

규칙:

- request id를 맞춘다.
- backend가 transport 오류로 죽으면 1회만 재시작한다.
- 판정 오류는 재시작하지 않고 사용자에게 그대로 보여준다.
- stderr는 개발 중에는 보이게, 릴리스에서는 로그 정책을 정한다.

### State model

UI 상태는 최소한 아래를 가진다.

```ts
type AuditState = "idle" | "scanning" | "complete" | "error";
type ConnectionState = "connecting" | "connected" | "error";
```

새 툴의 고유 상태를 추가해도, 큰 화면 상태는 이 흐름에서 벗어나지 않게 한다.

---

## 9. HiDPI와 선명도

이번 Attenuation Auditor 작업에서 가장 중요한 실전 교훈이다. 색과 레이아웃을 맞춰도, 125% Windows 배율에서 흐리면 제품 품질이 무너진다.

### Windows manifest

반드시 custom manifest를 포함한다.

```xml
<dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>
<dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2,PerMonitor</dpiAwareness>
<gdiScaling xmlns="http://schemas.microsoft.com/SMI/2017/WindowsSettings">false</gdiScaling>
<highResolutionScrollingAware xmlns="http://schemas.microsoft.com/SMI/2013/WindowsSettings">true</highResolutionScrollingAware>
```

### Process DPI

Windows에서는 앱 시작 초기에 Per Monitor V2 context를 적용한다.

```rust
#[cfg(target_os = "windows")]
fn enable_per_monitor_v2_dpi() {
    #[link(name = "user32")]
    extern "system" {
        fn SetProcessDpiAwarenessContext(value: isize) -> i32;
    }

    const DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2: isize = -4;
    unsafe {
        let _ = SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    }
}
```

### WebView 설정

```rust
window.set_zoom(1.0)?;
window.set_shadow(false)?;
```

`set_shadow(false)`는 borderless 창 최상단에 생길 수 있는 흰 1px 선을 막기 위해 검토한다. 그림자가 꼭 필요하면 실제 릴리스 캡처에서 100%, 125%, 150%를 다시 확인한다.

### QA 기준

- 1180 x 760 logical window가 125%에서 1475 x 950 physical pixels로 캡처되는지 확인한다.
- 텍스트, checkbox, icon stroke가 흐릿하거나 두껍게 뭉개지지 않아야 한다.
- low-res PNG 아이콘을 확대하지 않는다.
- 캡처는 README 또는 docs에 남겨 다음 회귀 비교 기준으로 쓴다.

---

## 10. 패키징과 Wwise 애드온 연결

### Tauri config

```json
{
  "app": {
    "windows": [{
      "width": 1180,
      "height": 760,
      "minWidth": 860,
      "minHeight": 600,
      "center": true,
      "resizable": true,
      "decorations": false,
      "shadow": false,
      "backgroundColor": "#090b0f"
    }]
  },
  "bundle": {
    "targets": ["nsis"],
    "category": "Music"
  }
}
```

### Backend resource

번들된 backend 실행파일은 Tauri resource로 포함한다.

```json
"resources": {
  "resources/auditor_backend.exe": "auditor_backend.exe"
}
```

설치본은 사용자별 앱 데이터 폴더에 예외/설정 데이터를 저장한다. 개발 폴더의 JSON을 직접 계속 쓰면 설치본과 개발본이 꼬일 수 있다.

### Wwise command add-on

Wwise Tools 메뉴 연결은 JSON command add-on으로 제공한다.

```json
{
  "version": 1,
  "commands": [{
    "id": "com.tools.my-wwise-tool",
    "displayName": "My Wwise Tool",
    "program": "%LOCALAPPDATA%\\My Wwise Tool\\my-tool.exe",
    "mainMenu": { "basePath": "Tools" }
  }]
}
```

규칙:

- displayName은 앱 타이틀과 동일하게 한다.
- command id는 툴별로 고유해야 한다.
- 설치 스크립트는 `%APPDATA%\Audiokinetic\Wwise\Add-ons\Commands`에 파일을 만든다.
- Wwise가 이미 켜져 있으면 메뉴 반영을 위해 재시작이 필요할 수 있음을 안내한다.

---

## 11. 카피와 언어

### 언어 전환

- KO/EN toggle은 titlebar에 둔다.
- 구조는 공유하고 문자열만 바꾼다.
- product name, brand title처럼 제품 정체성 문구는 한/영 모두 영문으로 고정할 수 있다.
- 기술 용어는 무리하게 번역하지 않는다. `Attenuation`, `Work Unit`, `WAAPI`, `Actor-Mixer Hierarchy`는 그대로 유지해도 된다.

### Wwise 툴 카피 공식

Idle body:

```text
Actor-Mixer Hierarchy를 따라 [기준 A]와 [기준 B]를 함께 검증합니다.
```

Scanning body:

```text
가장 가까운 override/effective 값을 해석하고 [검사 대상]을 확인합니다.
```

Complete body:

```text
결과를 선택하면 Wwise의 해당 오브젝트로 바로 이동할 수 있습니다.
```

Error:

```text
Wwise 연결 또는 WAAPI 응답을 확인하세요.
```

숫자를 반복하는 설명은 피한다. 큰 숫자는 이미 UI에 있으므로 body는 의미와 다음 행동을 말한다.

---

## 12. 새 Wwise 툴 제작 절차

1. 검사/작업 계약을 먼저 쓴다.

```text
입력: 어떤 Wwise object와 property를 읽는가
판정: 어떤 조건이면 normal / issue / exception인가
행동: select in Wwise, export, fix, exception 중 무엇을 제공하는가
금지: 바꾸면 안 되는 판정 단순화는 무엇인가
```

2. backend 테스트를 만든다.

- WAAPI 응답 fixture.
- normal, issue, exception, null/missing property.
- WorkUnit/Folder 같은 Wwise 특수 케이스.

3. UI shell을 복제한다.

- WindowChrome
- ProjectBar
- Hero
- ControlStrip
- MetricsStrip
- ScopeTree
- ResultsTable
- CriteriaModal

4. 고유 시각화를 만든다.

- 검사 대상의 형태를 한 줄 SVG 또는 단순 도형으로 추상화한다.
- scanning/complete/error 상태만 motion을 둔다.
- 데이터 의미 없는 장식은 제거한다.

5. Wwise action을 연결한다.

- selected row -> `ak.wwise.ui.commands.execute` 또는 object selection command.
- export -> dialog.
- exception/fix -> 명시적 버튼.

6. 패키징한다.

- Python backend를 exe로 묶는다.
- Tauri resource에 포함한다.
- NSIS installer를 만든다.
- Wwise command add-on script를 제공한다.

7. 시각 QA를 한다.

- 100%, 125%, 150% DPI.
- 860 x 600, 1180 x 760, maximized.
- KO/EN.
- connected/error/scanning/complete.

---

## 13. 출시 전 QA 체크리스트

### 시각

- [ ] 100%, 125%, 150% Windows scaling에서 흐릿하지 않다.
- [ ] 창 최상단에 흰 줄이 없다.
- [ ] 체크마크와 브랜드 그래픽이 벡터로 선명하다.
- [ ] muted text가 실제 모니터에서 읽힌다.
- [ ] hero, control strip, metrics, workspace의 세로 리듬이 유지된다.
- [ ] 최소 창에서 텍스트와 버튼이 겹치지 않는다.
- [ ] KO/EN 모두 ellipsis와 wrapping이 정상이다.

### Wwise

- [ ] Wwise 미실행 상태에서 연결 오류가 친절하게 표시된다.
- [ ] 연결 성공 시 project name과 hierarchy context가 보인다.
- [ ] scope lazy load가 실패해도 전체 앱이 멈추지 않는다.
- [ ] 선택한 result가 Wwise object selection으로 연결된다.
- [ ] export 경로 선택과 취소가 모두 정상이다.
- [ ] exception/fix 같은 상태 변경은 사용자가 명시적으로 누른 뒤 실행된다.

### 데이터 계약

- [ ] 판정 조건이 criteria modal, tests, docs에 같은 말로 적혀 있다.
- [ ] null GUID, missing property, inherited/effective property를 테스트했다.
- [ ] WorkUnit/PhysicalFolder 같은 Wwise 반환 특수 케이스를 처리한다.
- [ ] UI 편의를 위해 판정 조건을 단순화하지 않았다.
- [ ] 결과 수, score, table row가 같은 source of truth를 사용한다.

### 성능

- [ ] 긴 hierarchy scan 중 UI가 멈추지 않는다.
- [ ] scanning animation이 backend 작업을 방해하지 않는다.
- [ ] table row가 많아도 scroll이 버벅이지 않는다.
- [ ] repeated reconnect에서 backend zombie process가 남지 않는다.

### 접근성

- [ ] 모든 버튼에 focus-visible이 있다.
- [ ] icon-only button에 aria-label이 있다.
- [ ] 색만으로 issue를 구분하지 않는다.
- [ ] reduced motion이 적용된다.
- [ ] tab 순서가 작업 흐름과 맞다.

---

## 14. 금지 패턴

- 색상만 비슷하게 칠하고 정보 계층을 바꾸지 않는 것.
- Windows DPI awareness 없이 WebView를 배율 확대에 맡기는 것.
- 텍스트 `✓`, 저해상도 PNG, 확대된 bitmap icon을 쓰는 것.
- Wwise 판정 계약을 UI에서 즉석 계산으로 중복 구현하는 것.
- 스캔 중 실제 진행률을 모를 때 가짜 퍼센트를 보여주는 것.
- 빨강을 단순 강조색으로 쓰는 것.
- table만 있고 Wwise로 돌아가는 액션이 약한 것.
- help/criteria 없이 “왜 걸렸는지” 설명 못 하는 결과를 만드는 것.
- 한글에 영문용 넓은 letter-spacing을 그대로 적용하는 것.
- 창 버튼, titlebar drag, double click maximize 같은 데스크톱 기본 기대를 깨는 것.

---

## 15. Source of Truth

Attenuation Auditor V2 기준 위치:

| 파일 | 역할 |
|---|---|
| `src/styles.css` | 색상, 레이아웃, 컴포넌트, motion |
| `src/App.tsx` | 화면 상태 구조와 Wwise workflow |
| `src/components/WindowChrome.tsx` | custom titlebar, 언어, reconnect |
| `src/components/BrandMark.tsx` | 제품군 브랜드 그래픽 |
| `src/components/AttenuationOrbit.tsx` | Wwise 스캔 상태 그래픽 |
| `src/components/PrecisionCheck.tsx` | 고해상도 checkbox/check 표시 |
| `src/components/ScopeTree.tsx` | Wwise hierarchy 범위 선택 |
| `src/components/ResultsTable.tsx` | 결과 검토와 Wwise 액션 |
| `src/i18n.ts` | KO/EN 카피 |
| `auditor_core.py` | 판정 계약 |
| `auditor_backend.py` | WAAPI/backend command 처리 |
| `src-tauri/src/lib.rs` | persistent backend bridge, WebView zoom/shadow |
| `src-tauri/src/main.rs` | Windows Per Monitor V2 DPI context |
| `src-tauri/windows-app-manifest.xml` | DPI manifest |
| `src-tauri/tauri.conf.json` | 창/번들/리소스 설정 |

새 툴을 만들 때는 이 파일들을 복사해 이름만 바꾸는 방식보다, `계약`, `상태`, `컴포넌트`, `QA`를 먼저 맞춘 뒤 필요한 코드를 가져오는 방식을 권장한다.

---

## 16. 변경 기록 템플릿

```md
### YYYY-MM-DD · vX.Y

- 변경: 무엇을 바꿨는가
- 이유: 어떤 사용자 문제 또는 Wwise workflow 문제를 해결하는가
- 영향: 토큰 / 컴포넌트 / 번역 / WAAPI 계약 / 패키징 / 테스트 중 무엇이 바뀌는가
- 출처: FAMILY / WWISE / STD
- 회귀 확인: DPI, 창 크기, 언어, Wwise 연결 상태, fixture
```

디자인 결정은 "더 예뻐 보여서"가 아니라, 사용자가 Wwise 안에서 어떤 문제를 더 빨리, 더 정확하게 발견하고 행동하게 되는지까지 기록한다.
