import os
import tkinter.font as tkfont

VERSION         = "V.2.0.0"
WAAPI_URL       = "ws://127.0.0.1:8080/waapi"
SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
EXCEPTIONS_FILE = os.path.join(SCRIPT_DIR, "att_auditor_exceptions.json")

# ── Colors ────────────────────────────────────────────────────────────────────
# Stereo Auditor 제품군 디자인 토큰. Tk는 alpha/blur/gradient를 직접 지원하지
# 않으므로, 문서의 표면 합성 결과에 가까운 불투명 색으로 계층을 만든다.
BG        = "#090b0f"   # app background
BG2       = "#0d1015"   # surface / table
BG3       = "#11151c"   # raised surface / header
PANEL     = "#171c25"   # active control
FIELD     = "#080a0e"   # recessed field
BORDER    = "#1c212b"   # hairline (white 약 8%)
BORDER2   = "#293140"   # strong/focus hairline

ACCENT_CYAN   = "#55d5ef"
ACCENT        = "#6a86ff"
ACCENT_VIOLET = "#a869ff"
ACCENT_HI     = "#8299ff"
ACCENT_LO     = "#526ddb"
ON_ACCENT     = "#f7f9ff"

FG        = "#edf1f8"
FG_DIM    = "#a1aabc"
FG_MUT    = "#778195"
HOVER     = "#141922"
ROW_ALT   = "#0b0e13"
SEL_BG    = "#202b43"
SEL_FG    = "#f5f7ff"

# 상태색. miss/extra의 빨강/앰버 의미는 감사 판정 규칙이므로 유지한다.
OK_CLR  = ACCENT_CYAN
WARN    = "#eeb34f"
ERR_CLR = "#f06468"
EXC_CLR = ACCENT_VIOLET

# 상태 행 배경 틴트 (even/odd). 라벨과 함께 사용하여 색상에만 의존하지 않는다.
TINT_ERR_E,  TINT_ERR_O  = "#211318", "#1a1014"
TINT_WARN_E, TINT_WARN_O = "#211b10", "#1a160e"
TINT_EXC_E,  TINT_EXC_O  = "#1c1527", "#17121f"

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

FONT_H1   = [UI_BOLD_FAMILY, 12, UI_BOLD_WEIGHT]
FONT_H2   = [UI_BOLD_FAMILY, 11, UI_BOLD_WEIGHT]
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
# (bg, fg, hover, pressed) — Stereo Auditor의 compact control 계층
_BP = {
    "primary": (ACCENT,    ON_ACCENT, ACCENT_HI, ACCENT_LO),
    "ghost":   (BG3,       FG_DIM,    PANEL,     FIELD),
    "lang":    (PANEL,     FG_DIM,    BORDER2,   FIELD),
    "warn":    ("#211b10", WARN,      "#2b2313", "#17120c"),
    "exc":     ("#1c1527", EXC_CLR,   "#271b37", "#15101d"),
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
