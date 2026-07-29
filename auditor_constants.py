import os
import tkinter.font as tkfont

VERSION         = "V.1.4.0"
WAAPI_URL       = "ws://127.0.0.1:8080/waapi"
SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
EXCEPTIONS_FILE = os.path.join(SCRIPT_DIR, "att_auditor_exceptions.json")

# ── Colors ────────────────────────────────────────────────────────────────────
# SoundField 의 neutral(무채색) 테마를 그대로 이식. 아래 색은 SoundField
# theme.py 의 COLORS_GREY 와 1:1 대응한다 (괄호 안이 원래 키 이름).
BG        = "#1c1c1c"   # window            (bg)
BG2       = "#1f1f1f"   # panel / list      (bg_panel)
BG3       = "#262626"   # 올라온 면 / 헤더  (bg_elev)
PANEL     = "#2a2a2a"   # 컨트롤 강조       (bg_control_hi)
FIELD     = "#1a1a1a"   # 입력 필드         (bg_control)
BORDER    = "#303030"   #                   (border)
BORDER2   = "#3a3a3a"   #                   (border_strong)
ACCENT    = "#888888"   # 강조 — 무채색 통일 (accent)
ACCENT_HI = "#999999"   #                   (accent_hover)
ACCENT_LO = "#777777"   #                   (accent_pressed)
ON_ACCENT = "#1a1a1a"   # accent 채움 위의 글자색 (on_accent)
FG        = "#c8c8c8"   #                   (text)
# 아래 둘만 SoundField 값(#707070 / #4a4a4a)보다 밝게 올렸다. Tk 는 Qt 보다
# 글자를 얇게 그려서 같은 hex 라도 더 흐리게 보이기 때문 — 체감 밝기를 맞춘 값.
FG_DIM    = "#8a8a8a"   #                   (text_secondary 보정)
FG_MUT    = "#6a6a6a"   #                   (text_muted 보정)
HOVER     = "#232323"   #                   (hover / row_hover)
ROW_ALT   = "#1a1a1a"   #                   (row_alt)
SEL_BG    = "#303030"   # 선택 행 — 무채색이라 한 단계 밝게 (row_playing)
SEL_FG    = "#e8e8e8"   # 선택 행 글자

# 상태색 — 검수 결과 구분이 색으로 남아야 하므로 채도만 낮춰 유지한다.
OK_CLR  = "#6fb58a"   # 정상
WARN    = "#d2a24e"   # 경고 / 초과
ERR_CLR = "#c44848"   # 위반 / 누락
EXC_CLR = "#9c7fc7"   # 예외 등록

# 상태 행 배경 틴트 (even/odd 지브라) — 무채색 배경에 얹는 아주 옅은 색조
TINT_ERR_E,  TINT_ERR_O  = "#241a1a", "#1f1717"
TINT_WARN_E, TINT_WARN_O = "#242018", "#1f1c16"
TINT_EXC_E,  TINT_EXC_O  = "#221f28", "#1d1b22"

# ── Fonts ─────────────────────────────────────────────────────────────────────
# SoundField 와 동일한 우선순위. Tkinter 는 QSS 처럼 자동 폴백이 없어서
# init_fonts(root) 에서 실제 설치된 것을 골라 아래 리스트를 in-place 로 채운다.
# 튜플이 아니라 리스트여야 한다 — from ... import 로 값을 가져간 쪽에도
# 같은 객체가 공유되어 확정 결과가 그대로 반영된다.
# 보통 굵기는 Pretendard Medium. Tk 가 Pretendard Regular 를 9pt 에서 너무
# 얇게 그려 글자가 뿌옇게 보이기 때문.
_UI_STACK   = ["Pretendard Medium", "Pretendard", "Segoe UI Variable Text",
               "Segoe UI", "Malgun Gothic", "Tahoma"]
_MONO_STACK = ["Cascadia Code", "Cascadia Mono", "Consolas", "Courier New"]

# 굵은 글씨는 (글꼴, 굵기) 짝으로 고른다. Pretendard 에는 Bold 면이 없어서
# weight="bold" 를 주면 Windows 가 Regular 를 부풀려 가짜 볼드를 만들고,
# 그게 번져서 안개처럼 뿌옇게 보인다. 실제로 존재하는 SemiBold 면을
# weight="normal" 로 쓰면 합성이 일어나지 않아 깨끗하다.
# 폴백으로 내려가는 글꼴들은 진짜 Bold 면이 있으므로 "bold" 를 준다.
_UI_BOLD_STACK = [("Pretendard SemiBold",   "normal"),
                  ("Segoe UI Variable Text", "bold"),
                  ("Segoe UI",               "bold"),
                  ("Malgun Gothic",          "bold"),
                  ("Tahoma",                 "bold")]

UI_FAMILY      = "Segoe UI"    # 보통 굵기 — init_fonts() 에서 확정
UI_BOLD_FAMILY = "Segoe UI"    # 굵은 글씨 — init_fonts() 에서 확정
UI_BOLD_WEIGHT = "bold"        # 굵은 글씨용 weight — init_fonts() 에서 확정
MONO_FAMILY    = "Consolas"    # init_fonts() 에서 확정

FONT_H1   = [UI_BOLD_FAMILY, 11, UI_BOLD_WEIGHT]
FONT_H2   = [UI_BOLD_FAMILY, 10, UI_BOLD_WEIGHT]
FONT_UI   = [UI_FAMILY,  9]
FONT_UIB  = [UI_BOLD_FAMILY,  9, UI_BOLD_WEIGHT]
FONT_SM   = [UI_FAMILY,  8]
FONT_CODE = [MONO_FAMILY, 9]

_UI_FONTS      = (FONT_UI, FONT_SM)
_UI_BOLD_FONTS = (FONT_H1, FONT_H2, FONT_UIB)
_MONO_FONTS    = (FONT_CODE,)
_FONTS_READY   = False


def _pick_family(root, stack):
    """stack 순서대로 실제 설치된 첫 폰트를 고른다. 못 찾으면 마지막 후보."""
    try:
        available = set(tkfont.families(root))
    except Exception:
        return stack[-1]
    for family in stack:
        if family in available:
            return family
    return stack[-1]


def _pick_bold(root, stack):
    """(글꼴, 굵기) 후보 중 실제 설치된 첫 짝을 고른다."""
    try:
        available = set(tkfont.families(root))
    except Exception:
        return stack[-1]
    for pair in stack:
        if pair[0] in available:
            return pair
    return stack[-1]


def init_fonts(root):
    """root 생성 직후 · 위젯 생성 전에 한 번 호출한다."""
    global UI_FAMILY, UI_BOLD_FAMILY, UI_BOLD_WEIGHT, MONO_FAMILY, _FONTS_READY
    if _FONTS_READY:
        return
    UI_FAMILY   = _pick_family(root, _UI_STACK)
    MONO_FAMILY = _pick_family(root, _MONO_STACK)
    UI_BOLD_FAMILY, UI_BOLD_WEIGHT = _pick_bold(root, _UI_BOLD_STACK)
    for spec in _UI_FONTS:
        spec[0] = UI_FAMILY
    for spec in _UI_BOLD_FONTS:
        spec[0] = UI_BOLD_FAMILY
        spec[2] = UI_BOLD_WEIGHT
    for spec in _MONO_FONTS:
        spec[0] = MONO_FAMILY
    # messagebox / 메뉴 등 Tk 내장 위젯도 같은 폰트를 쓰게 맞춘다.
    for name, size, fam, wt in (("TkDefaultFont", 9, UI_FAMILY, "normal"),
                                ("TkTextFont", 9, UI_FAMILY, "normal"),
                                ("TkMenuFont", 9, UI_FAMILY, "normal"),
                                ("TkHeadingFont", 9, UI_BOLD_FAMILY, UI_BOLD_WEIGHT),
                                ("TkTooltipFont", 8, UI_FAMILY, "normal")):
        try:
            tkfont.nametofont(name, root=root).configure(family=fam, size=size, weight=wt)
        except Exception:
            pass
    try:
        tkfont.nametofont("TkFixedFont", root=root).configure(family=MONO_FAMILY, size=9)
    except Exception:
        pass
    _FONTS_READY = True


def ui_font(size=9, bold=False):
    """확정된 UI 폰트로 임의 크기의 스펙을 만든다."""
    if bold:
        return [UI_BOLD_FAMILY, size, UI_BOLD_WEIGHT]
    return [UI_FAMILY, size]


def mono_font(size=9, bold=False):
    spec = [MONO_FAMILY, size]
    if bold:
        spec.append("bold")
    return spec


# ── Button presets ────────────────────────────────────────────────────────────
# (bg, fg, hover, pressed) — SoundField QPushButton / QPushButton#primary 대응
_BP = {
    "primary": (ACCENT,    ON_ACCENT, ACCENT_HI, ACCENT_LO),
    "ghost":   (BG3,       FG,        PANEL,     FIELD),
    "lang":    (BG2,       "#9a9a9a", BG3,       FIELD),
    "warn":    ("#241d10", WARN,      "#2c2415", "#1c1710"),
    "exc":     ("#221f28", EXC_CLR,   "#2a2632", "#1c1a22"),
}

FIND_CMD_PRIMARY = ["FindInProjectExplorerSelectionChannel1",
                    "FindInProjectExplorer", "FindInProjectExplorer1"]

CONTAINER_TYPES  = ["ActorMixer", "RandomSequenceContainer",
                    "BlendContainer", "SwitchContainer"]
SCOPE_TREE_TYPES = {"WorkUnit", "PhysicalFolder", "ActorMixer",
                    "RandomSequenceContainer", "BlendContainer",
                    "SwitchContainer", "Folder"}
_DUMMY_SUFFIX    = "__dummy__"

_ICON_MAP = {
    "Sound":                   "ObjectIcons_SoundFX_nor.png",
    "RandomSequenceContainer": "ObjectIcons_RandomSequenceContainer_nor.png",
    "BlendContainer":          "ObjectIcons_BlendContainer_nor.png",
    "SwitchContainer":         "ObjectIcons_SwitchContainer_nor.png",
    "ActorMixer":              "ObjectIcons_ActorMixer_nor.png",
    "Folder":                  "ObjectIcons_Folder_nor.png",
    "WorkUnit":                "ObjectIcons_Workunit_nor.png",
    "PhysicalFolder":          "ObjectIcons_PhysicalFolder_nor.png",
}

_ICON_FALLBACK = {
    "WorkUnit":                "⬡",
    "PhysicalFolder":          "📁",
    "ActorMixer":              "⊕",
    "Folder":                  "▷",
    "RandomSequenceContainer": "⊞",
    "BlendContainer":          "⊟",
    "SwitchContainer":         "⊠",
}
