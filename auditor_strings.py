# 한·영 UI 문자열. 코드 상수가 아닌 사용자 표시 텍스트만.

_S = {
    "ko": {
        "reconnect":         "⟳  재연결",
        "help_btn":          "?  도움말",
        "lang_toggle":       "EN",
        "connecting":        "Wwise 연결 중...",
        "connected":         "연결됨",
        "connect_fail":      "연결 실패  —  WAAPI 활성화 필요  ({})",
        "no_waapi":          "waapi-client 미설치  →  install.bat 실행",
        "scan_btn":          "▶  스캔 실행",
        "audit_setup":       "AUDIT SETUP",
        "audit_desc":        "3D 포지셔닝과 Attenuation 연결 상태의 불일치를 함께 검사합니다.",
        "metric_checked":    "검사 오브젝트",
        "metric_violations": "위반",
        "metric_exceptions": "예외",
        "scanning":          "스캔 중...",
        "scan_done":         "스캔 완료  ·  {}개 검사  ·  위반 {}개",
        "scan_fail":         "스캔 실패: {}",
        "no_wwise":          "Wwise에 연결되지 않았습니다.",
        "no_type":           "오브젝트 타입을 하나 이상 선택하세요.",
        "no_results":        "내보낼 결과가 없습니다.",
        "no_violations":     "{}개 검사  ·  위반 없음  ✓",
        "violations_fmt":    "위반  {}개",
        "view_wwise":        "⊙  Wwise에서 보기",
        "export_csv":        "↓  CSV 내보내기",
        "select_item":       "항목을 선택하세요.",
        "not_found":         "Wwise에서 오브젝트를 선택할 수 없었습니다.",
        "csv_done":          "저장 완료:\n{}",
        "csv_title":         "CSV로 내보내기",
        "error_title":       "오류",
        "info_title":        "안내",
        "opt_sounds":        "Sound",
        "opt_containers":    "컨테이너  (ActorMixer / Random / Blend / Switch)",
        "obj_types_hdr":     "오브젝트 타입",
        "col_name":          "에셋 이름",
        "col_type":          "타입",
        "col_3d":            "3D 모드",
        "col_att":           "Attenuation",
        "col_issue":         "위반 유형",
        "col_wu":            "Work Unit",
        "col_path":          "전체 경로",
        "issue_miss":        "Attenuation 미설정",
        "issue_extra":       "2D에 ATT 연결",
        "scope_hdr":         "스캔 범위",
        "scope_hint":        "미선택 시 전체 스캔",
        "scope_refresh":     "↺",
        "scope_all_lbl":     "전체",
        "scope_sel_lbl":     "{}개 선택됨",
        "scope_empty":       "Wwise 연결 후 표시됩니다.",
        "scope_loading":     "불러오는 중...",
        "scope_root_lbl":    "전체  (Actor-Mixer Hierarchy)",
        "tab_violations":    "위반 목록",
        "tab_exceptions":    "예외 처리",
        "add_exception":     "+ 예외 처리",
        "remove_exception":  "× 예외 해제",
        "select_to_except":  "위반 목록에서 예외 처리할 항목을 선택하세요.",
        "select_to_unexcept":"예외 처리 탭에서 해제할 항목을 선택하세요.",
        "no_exceptions":     "예외 처리 항목이 없습니다.",
        "exc_count":         "예외  {}개",
        "help_title":        "Attenuation Auditor — 사용 방법",
        "help_body": (
            "【 연결 】\n"
            "• Wwise 실행 후 WAAPI 활성화\n"
            "  (Project > User Preferences > Enable WAAPI)\n"
            "• ⟳ 재연결 버튼으로 연결\n"
            "\n"
            "【 스캔 】\n"
            "• ▶ 스캔 실행 버튼을 누르면 두 종류의 위반을 한 번에 검사합니다:\n"
            "  - 빨강 (miss)  : 3D 사운드인데 Attenuation 이 미설정\n"
            "  - 노랑 (extra) : 2D 사운드인데 Attenuation 이 연결됨\n"
            "• 판정은 @OverridePositioning=true 인 가장 가까운 조상의\n"
            "  값을 기준으로 합니다 (effective 노드).\n"
            "\n"
            "【 스캔 범위 】\n"
            "• 왼쪽 트리에서 워크유닛 또는 컨테이너를 선택해 범위 지정.\n"
            "• 아무것도 선택하지 않으면 전체 프로젝트를 스캔합니다.\n"
            "• ↺ 버튼으로 트리를 새로고침할 수 있습니다.\n"
            "• 노드를 드래그하면 좌우 패널 너비를 조절할 수 있습니다.\n"
            "\n"
            "【 예외 처리 】\n"
            "• 의도적인 위반 항목을 선택해 '+ 예외 처리' 클릭으로 등록.\n"
            "• 여러 항목 동시 선택 후 일괄 예외 처리 가능.\n"
            "• 예외 항목은 재스캔 시에도 위반으로 표시되지 않습니다.\n"
            "• 3D 모드·Attenuation·위반 유형이 바뀌면 자동 무효화됩니다.\n"
            "\n"
            "【 컬럼 】\n"
            "• 헤더 클릭: 해당 컬럼 기준 정렬\n"
            "• 헤더 드래그: 컬럼 순서 변경\n"
            "\n"
            "【 결과 색상 】\n"
            "• 빨강  —  Attenuation 미설정 (3D 오브젝트)\n"
            "• 노랑  —  2D 오브젝트에 Attenuation 연결\n"
            "• 보라  —  예외 처리 항목\n"
        ),
    },
    "en": {
        "reconnect":         "⟳  Reconnect",
        "help_btn":          "?  Help",
        "lang_toggle":       "KO",
        "connecting":        "Connecting to Wwise...",
        "connected":         "Connected",
        "connect_fail":      "Connection failed  —  Enable WAAPI  ({})",
        "no_waapi":          "waapi-client not installed  →  run install.bat",
        "scan_btn":          "▶  Run Scan",
        "audit_setup":       "AUDIT SETUP",
        "audit_desc":        "Checks 3D positioning and Attenuation linkage for mismatches.",
        "metric_checked":    "OBJECTS CHECKED",
        "metric_violations": "VIOLATIONS",
        "metric_exceptions": "EXCEPTIONS",
        "scanning":          "Scanning...",
        "scan_done":         "Scan done  ·  {} checked  ·  {} violations",
        "scan_fail":         "Scan failed: {}",
        "no_wwise":          "Not connected to Wwise.",
        "no_type":           "Select at least one object type.",
        "no_results":        "No results to export.",
        "no_violations":     "{} checked  ·  No violations  ✓",
        "violations_fmt":    "{} violations",
        "view_wwise":        "⊙  View in Wwise",
        "export_csv":        "↓  Export CSV",
        "select_item":       "Please select an item.",
        "not_found":         "Could not select object in Wwise.",
        "csv_done":          "Saved:\n{}",
        "csv_title":         "Export as CSV",
        "error_title":       "Error",
        "info_title":        "Info",
        "opt_sounds":        "Sound",
        "opt_containers":    "Container  (ActorMixer / Random / Blend / Switch)",
        "obj_types_hdr":     "Object Types",
        "col_name":          "Asset Name",
        "col_type":          "Type",
        "col_3d":            "3D Mode",
        "col_att":           "Attenuation",
        "col_issue":         "Issue",
        "col_wu":            "Work Unit",
        "col_path":          "Full Path",
        "issue_miss":        "Missing Attenuation",
        "issue_extra":       "2D + ATT linked",
        "scope_hdr":         "Scan Scope",
        "scope_hint":        "no selection = scan all",
        "scope_refresh":     "↺",
        "scope_all_lbl":     "All",
        "scope_sel_lbl":     "{} selected",
        "scope_empty":       "Connect to Wwise to populate.",
        "scope_loading":     "Loading...",
        "scope_root_lbl":    "All  (Actor-Mixer Hierarchy)",
        "tab_violations":    "Violations",
        "tab_exceptions":    "Exceptions",
        "add_exception":     "+ Add Exception",
        "remove_exception":  "× Remove Exception",
        "select_to_except":  "Select items from the violations list.",
        "select_to_unexcept":"Select items from the exceptions list.",
        "no_exceptions":     "No exceptions configured.",
        "exc_count":         "{} exceptions",
        "help_title":        "Attenuation Auditor — How to Use",
        "help_body": (
            "【 Connect 】\n"
            "• Launch Wwise and enable WAAPI\n"
            "  (Project > User Preferences > Enable WAAPI)\n"
            "• Click ⟳ Reconnect\n"
            "\n"
            "【 Scan 】\n"
            "• Pressing ▶ Run Scan detects both violations at once:\n"
            "  - Red  (miss)  : 3D sound without Attenuation\n"
            "  - Yellow (extra) : 2D sound with Attenuation linked\n"
            "• Decision uses the nearest ancestor (including self) with\n"
            "  @OverridePositioning = true (the effective node).\n"
            "\n"
            "【 Scan Scope 】\n"
            "• Select Work Units or containers in the left tree to limit scan scope.\n"
            "• No selection = scan entire project.\n"
            "• Use ↺ to refresh after project changes.\n"
            "• Drag the sash to resize the left/right panels.\n"
            "\n"
            "【 Exceptions 】\n"
            "• Select one or more violations → click '+ Add Exception'.\n"
            "• Exceptions persist across scans until manually removed.\n"
            "• Auto-invalidated if 3D mode, Attenuation, or issue type changes.\n"
            "\n"
            "【 Columns 】\n"
            "• Click header: sort by that column\n"
            "• Drag header: reorder columns\n"
            "\n"
            "【 Row Colors 】\n"
            "• Red    —  Missing Attenuation (3D object)\n"
            "• Yellow —  Attenuation linked on 2D object\n"
            "• Purple —  Exception (intentional violation)\n"
        ),
    },
}
