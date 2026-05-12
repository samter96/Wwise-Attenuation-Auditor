import os

VERSION         = "V.1.4.0"
WAAPI_URL       = "ws://127.0.0.1:8080/waapi"
SCRIPT_DIR      = os.path.dirname(os.path.abspath(__file__))
EXCEPTIONS_FILE = os.path.join(SCRIPT_DIR, "att_auditor_exceptions.json")

# ── Colors ────────────────────────────────────────────────────────────────────
BG      = "#0D1117"
BG2     = "#161B22"
BG3     = "#1C2128"
PANEL   = "#21262D"
BORDER  = "#30363D"
BORDER2 = "#444C56"
ACCENT  = "#58A6FF"
OK_CLR  = "#3FB950"
WARN    = "#D29922"
ERR_CLR = "#F85149"
FG      = "#E6EDF3"
FG_DIM  = "#8B949E"
FG_MUT  = "#484F58"
SEL_BG  = "#1F6FEB"
EXC_CLR = "#BC8CFF"

# ── Fonts ─────────────────────────────────────────────────────────────────────
_UI = "Segoe UI"
_MN = "Consolas"
FONT_H1   = (_UI, 11, "bold")
FONT_H2   = (_UI, 10, "bold")
FONT_UI   = (_UI,  9)
FONT_UIB  = (_UI,  9, "bold")
FONT_SM   = (_UI,  8)
FONT_CODE = (_MN,  9)

# ── Button presets ────────────────────────────────────────────────────────────
_BP = {
    "primary": ("#1F6FEB", "#FFFFFF", "#388BFD", "#1158C7"),
    "ghost":   (PANEL,     FG,        "#2D333B", BG3),
    "lang":    ("#1E1833", "#BC8CFF", "#271F42", "#140F24"),
    "warn":    ("#2D1B00", WARN,      "#3D2500", "#1A1000"),
    "exc":     ("#1E1B33", EXC_CLR,   "#27224A", "#140F24"),
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
