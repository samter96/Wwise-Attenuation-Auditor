#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading, time, socket, csv, os, json
import glob as _glob

try:
    from waapi import WaapiClient
    WAAPI_AVAILABLE = True
except ImportError:
    WAAPI_AVAILABLE = False

from auditor_constants import (
    VERSION, WAAPI_URL, SCRIPT_DIR, EXCEPTIONS_FILE,
    BG, BG2, BG3, PANEL, BORDER, BORDER2, ACCENT, OK_CLR, WARN, ERR_CLR,
    FG, FG_DIM, FG_MUT, SEL_BG, EXC_CLR,
    FONT_H1, FONT_H2, FONT_UI, FONT_UIB, FONT_SM, FONT_CODE,
    _BP, FIND_CMD_PRIMARY, CONTAINER_TYPES, SCOPE_TREE_TYPES,
    _DUMMY_SUFFIX, _ICON_MAP, _ICON_FALLBACK,
)
from auditor_strings import _S
from auditor_ui_helpers import _ab


class AttenuationAuditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Attenuation Auditor  —  Wwise")
        sh    = self.root.winfo_screenheight()
        win_h = int(sh * 0.80)
        win_w = max(1160, int(win_h * 1.55))
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.minsize(980, 620)
        self.root.configure(bg=BG)

        self.client            = None
        self._was_connected    = False
        self._find_cmd         = None
        self._results          = []
        self._total_checked    = 0
        self._scanned          = False
        self._proj_name        = ""
        self._lang             = "ko"
        self._cur_status_key   = None
        self._cur_status_args  = ()
        self._cur_status_color = FG_DIM
        self._hover_iid        = None
        self._hover_exc_iid    = None
        self._sort_col         = None
        self._sort_rev         = False
        self._exc_order        = []
        self._type_icons       = {}

        self._col_dragging  = False
        self._col_drag_id   = None
        self._col_drag_x    = 0
        self._col_order = ["name", "type", "spat", "att", "issue", "wu", "path"]

        self._opt_sounds     = tk.BooleanVar(value=True)
        self._opt_containers = tk.BooleanVar(value=True)

        self._scope_node_paths  = {}
        self._scope_node_loaded = {}
        self._exceptions = {}
        self._load_exceptions()

        self._apply_styles()
        self._build_ui()
        self._load_type_icons()
        self._start_wwise_watchdog()
        self.root.after(200, lambda: threading.Thread(
            target=self._connect_waapi, daemon=True).start())

    def _t(self, key):
        return _S[self._lang].get(key, _S["ko"].get(key, key))

    def _toggle_lang(self):
        self._lang = "en" if self._lang == "ko" else "ko"
        self._refresh_lang()

    def _refresh_lang(self):
        self._lang_btn.config(text=self._t("lang_toggle"))
        self._btn_reconnect.config(text=self._t("reconnect"))
        self._btn_help.config(text=self._t("help_btn"))
        self._btn_scan.config(text=self._t("scan_btn"))
        self._btn_view.config(text=self._t("view_wwise"))
        self._btn_export.config(text=self._t("export_csv"))
        self._btn_add_exc.config(text=self._t("add_exception"))
        self._btn_rem_exc.config(text=self._t("remove_exception"))
        self._lbl_obj_types.config(text=self._t("obj_types_hdr"))
        self._chk_sounds.config(text=self._t("opt_sounds"))
        self._chk_containers.config(text=self._t("opt_containers"))
        self._lbl_scope_hdr.config(text=self._t("scope_hdr"))
        self._lbl_scope_hint.config(text=self._t("scope_hint"))
        self._update_scope_label()
        self._nb.tab(0, text=f"  {self._t('tab_violations')}  ")
        self._nb.tab(1, text=f"  {self._t('tab_exceptions')}  ")
        col_keys = {"name": "col_name", "type": "col_type", "spat": "col_3d",
                    "att": "col_att", "issue": "col_issue",
                    "wu": "col_wu", "path": "col_path"}
        for cid, key in col_keys.items():
            self._tree.heading(cid, text=self._t(key))
            self._exc_tree.heading(cid, text=self._t(key))
        self._populate_results()
        self._populate_exceptions()
        if self._cur_status_key:
            try:
                msg = self._t(self._cur_status_key)
                if self._cur_status_args: msg = msg.format(*self._cur_status_args)
                self._status_lbl.config(text=msg, fg=self._cur_status_color)
                self._status_dot.config(fg=self._cur_status_color)
            except: pass

    def _apply_styles(self):
        s = ttk.Style(); s.theme_use("clam")
        s.configure("Treeview", background=BG2, foreground=FG, fieldbackground=BG2, rowheight=26, font=FONT_CODE, borderwidth=0, relief="flat")
        s.configure("Treeview.Heading", background=BG3, foreground=FG_DIM, font=FONT_UIB, relief="flat", padding=[8, 6])
        s.map("Treeview", background=[("selected", SEL_BG)], foreground=[("selected", "#FFFFFF")])
        s.map("Treeview.Heading", background=[("active", PANEL)])
        s.configure("Scope.Treeview", background=BG2, foreground=FG, fieldbackground=BG2, rowheight=22, font=FONT_UI, borderwidth=0, relief="flat")
        s.map("Scope.Treeview", background=[("selected", SEL_BG)], foreground=[("selected", "#FFFFFF")])
        s.configure("TNotebook", background=BG3, borderwidth=0, tabmargins=[0, 0, 0, 0])
        s.configure("TNotebook.Tab", background=BG3, foreground=FG_DIM, padding=[14, 7], font=FONT_UIB, borderwidth=0)
        s.map("TNotebook.Tab", background=[("selected", BG2), ("active", PANEL)], foreground=[("selected", FG), ("active", FG)])
        for orient in ("Vertical", "Horizontal"):
            s.configure(f"{orient}.TScrollbar", background=PANEL, troughcolor=BG2, arrowcolor=FG_DIM, borderwidth=0, relief="flat", width=8)
            s.map(f"{orient}.TScrollbar", background=[("active", BORDER2)])

    def _load_type_icons(self):
        candidates = _glob.glob(r"C:\Audiokinetic\*\Authoring\Data\Themes\classic\images\ObjectIcons")
        if not candidates: return
        d = candidates[-1]
        for ttype, fname in _ICON_MAP.items():
            p = os.path.join(d, fname)
            if os.path.exists(p):
                try: self._type_icons[ttype] = tk.PhotoImage(file=p)
                except: pass

    def _type_icon(self, obj_type):
        return self._type_icons.get(obj_type)

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=BG3, height=52); hdr.pack(fill="x"); hdr.pack_propagate(False)
        id_f = tk.Frame(hdr, bg=BG3); id_f.pack(side="left", padx=(16, 0))
        tk.Label(id_f, text="◉", bg=BG3, fg=ACCENT, font=(FONT_UI, 16)).pack(side="left", padx=(0, 8))
        tk.Label(id_f, text="Attenuation Auditor", bg=BG3, fg=FG, font=FONT_H1).pack(side="left")
        tk.Label(id_f, text=f"  {VERSION}", bg=BG3, fg=FG_MUT, font=FONT_SM).pack(side="left", pady=(3, 0))
        
        btn_area = tk.Frame(hdr, bg=BG3); btn_area.pack(side="right", padx=(0, 12))
        self._lang_btn = _ab(btn_area, self._t("lang_toggle"), self._toggle_lang, preset="lang", padx=12)
        self._lang_btn.pack(side="right", padx=(4, 0), pady=10)
        self._btn_reconnect = _ab(btn_area, self._t("reconnect"), lambda: threading.Thread(target=self._connect_waapi, daemon=True).start(), preset="ghost", font=FONT_UI, padx=12)
        self._btn_reconnect.pack(side="right", padx=4, pady=10)
        self._btn_help = _ab(btn_area, self._t("help_btn"), self._show_help, preset="ghost", font=FONT_UI, padx=12)
        self._btn_help.pack(side="right", pady=10)

        status_area = tk.Frame(hdr, bg=BG3); status_area.pack(side="left", fill="x", expand=True, padx=20)
        self._status_dot = tk.Label(status_area, text="●", bg=BG3, fg=FG_MUT, font=(FONT_UI, 10)); self._status_dot.pack(side="left", padx=(0, 6))
        self._proj_lbl = tk.Label(status_area, text="", bg=BG3, fg=ACCENT, font=FONT_UIB); self._proj_lbl.pack(side="left")
        self._proj_sep = tk.Label(status_area, text="", bg=BG3, fg=FG_MUT, font=FONT_UI); self._proj_sep.pack(side="left", padx=(4, 4))
        self._status_lbl = tk.Label(status_area, text="초기화 중...", bg=BG3, fg=FG_DIM, font=FONT_UI, anchor="w"); self._status_lbl.pack(side="left", fill="x")

        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")
        content = tk.Frame(self.root, bg=BG); content.pack(fill="both", expand=True)

        opt_outer = tk.Frame(content, bg=BORDER); opt_outer.pack(fill="x", padx=12, pady=(10, 0))
        opt_panel = tk.Frame(opt_outer, bg=BG2); opt_panel.pack(fill="both", padx=1, pady=(0, 1))
        tk.Frame(opt_panel, bg=ACCENT, height=2).pack(fill="x")
        opt_body = tk.Frame(opt_panel, bg=BG2); opt_body.pack(fill="x", padx=14, pady=10)
        row = tk.Frame(opt_body, bg=BG2); row.pack(fill="x")

        grp2 = tk.Frame(row, bg=BG2); grp2.pack(side="left", anchor="nw")
        self._lbl_obj_types = tk.Label(grp2, text=self._t("obj_types_hdr"), bg=BG2, fg=FG_DIM, font=FONT_SM); self._lbl_obj_types.pack(anchor="w", pady=(0, 4))
        self._chk_sounds = tk.Checkbutton(grp2, text=self._t("opt_sounds"), variable=self._opt_sounds, bg=BG2, fg=FG, selectcolor=PANEL, activebackground=BG2, activeforeground=FG, font=FONT_UI, anchor="w", cursor="hand2"); self._chk_sounds.pack(anchor="w")
        self._chk_containers = tk.Checkbutton(grp2, text=self._t("opt_containers"), variable=self._opt_containers, bg=BG2, fg=FG, selectcolor=PANEL, activebackground=BG2, activeforeground=FG, font=FONT_UI, anchor="w", cursor="hand2"); self._chk_containers.pack(anchor="w", pady=(3, 0))

        self._btn_scan = _ab(row, self._t("scan_btn"), self._run_scan, preset="primary", font=FONT_UIB, padx=24); self._btn_scan.pack(side="right", anchor="center")

        paned = tk.PanedWindow(content, orient="horizontal", bg=BORDER, sashwidth=5, sashrelief="flat", sashpad=0, bd=0)
        paned.pack(fill="both", expand=True, padx=12, pady=(6, 0))

        left = tk.Frame(paned, bg=BG2, width=220); paned.add(left, minsize=140)
        tk.Frame(left, bg=ACCENT, height=2).pack(fill="x")
        scope_hdr_f = tk.Frame(left, bg=BG3); scope_hdr_f.pack(fill="x")
        self._lbl_scope_hdr = tk.Label(scope_hdr_f, text=self._t("scope_hdr"), bg=BG3, fg=FG_DIM, font=FONT_UIB, padx=8, pady=6); self._lbl_scope_hdr.pack(side="left")
        self._btn_scope_refresh = tk.Button(scope_hdr_f, text=self._t("scope_refresh"), command=lambda: threading.Thread(target=self._load_scope_tree, daemon=True).start(), bg=BG3, fg=FG_DIM, relief="flat", bd=0, font=(FONT_UI, 11), padx=6, pady=3, cursor="hand2", activebackground=PANEL, activeforeground=FG); self._btn_scope_refresh.pack(side="right", padx=(0, 4), pady=4)
        self._lbl_scope_sel = tk.Label(scope_hdr_f, text=self._t("scope_all_lbl"), bg=BG3, fg=FG_MUT, font=FONT_SM, pady=6); self._lbl_scope_sel.pack(side="right", padx=(0, 2))
        self._lbl_scope_hint = tk.Label(left, text=self._t("scope_hint"), bg=BG2, fg=FG_MUT, font=FONT_SM, pady=2); self._lbl_scope_hint.pack(fill="x", padx=8)
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x")
        scope_tree_f = tk.Frame(left, bg=BG2); scope_tree_f.pack(fill="both", expand=True)
        scope_vsb = ttk.Scrollbar(scope_tree_f, orient="vertical"); scope_vsb.pack(side="right", fill="y")
        self._scope_tree = ttk.Treeview(scope_tree_f, style="Scope.Treeview", show="tree", selectmode="extended")
        self._scope_tree.configure(yscrollcommand=scope_vsb.set); scope_vsb.config(command=self._scope_tree.yview); self._scope_tree.pack(fill="both", expand=True)
        self._scope_tree.tag_configure("dim", foreground=FG_MUT)
        self._scope_tree.bind("<<TreeviewOpen>>", self._on_scope_expand); self._scope_tree.bind("<<TreeviewSelect>>", self._on_scope_select)
        self._scope_placeholder = self._scope_tree.insert("", "end", text=f"  {self._t('scope_empty')}", tags=("dim",))

        right = tk.Frame(paned, bg=BG); paned.add(right, minsize=400)
        self._nb = ttk.Notebook(right); self._nb.pack(fill="both", expand=True)

        vio_frame = tk.Frame(self._nb, bg=BG2); self._nb.add(vio_frame, text=f"  {self._t('tab_violations')}  ")
        vio_hdr = tk.Frame(vio_frame, bg=BG3); vio_hdr.pack(fill="x")
        self._lbl_count = tk.Label(vio_hdr, text="—", bg=BG3, fg=FG_DIM, font=FONT_UI, padx=12, pady=5); self._lbl_count.pack(side="right")
        tk.Frame(vio_frame, bg=BORDER, height=1).pack(fill="x")
        tree_f = tk.Frame(vio_frame, bg=BG2); tree_f.pack(fill="both", expand=True)
        cols = ("name", "type", "spat", "att", "issue", "wu", "path")
        self._tree = ttk.Treeview(tree_f, columns=cols, show="headings", selectmode="extended")
        vsb = ttk.Scrollbar(tree_f, orient="vertical", command=self._tree.yview); hsb = ttk.Scrollbar(tree_f, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set); vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x"); self._tree.pack(fill="both", expand=True)
        col_cfg = [("name","col_name",240,True),("type","col_type",160,False),("spat","col_3d",160,False),("att","col_att",200,False),("issue","col_issue",160,False),("wu","col_wu",140,False),("path","col_path",400,True)]
        for cid, hkey, width, stretch in col_cfg:
            self._tree.heading(cid, text=self._t(hkey), command=lambda c=cid: self._sort_by(c))
            self._tree.column(cid, width=width, stretch=tk.YES if stretch else tk.NO, anchor="w")
        self._tree.configure(displaycolumns=self._col_order)
        self._tree.tag_configure("miss_e", background="#1A0A0A", foreground=ERR_CLR); self._tree.tag_configure("miss_o", background="#150808", foreground=ERR_CLR)
        self._tree.tag_configure("extra_e", background="#1A1500", foreground=WARN); self._tree.tag_configure("extra_o", background="#151100", foreground=WARN)
        self._tree.tag_configure("ok_msg", background=BG2, foreground=OK_CLR); self._tree.tag_configure("hover", font=(*FONT_CODE[:2], "bold"))
        self._tree.bind("<Double-1>", self._on_double_click); self._tree.bind("<Motion>", self._on_hover); self._tree.bind("<Leave>", self._on_leave)
        self._tree.bind("<ButtonPress-1>", self._on_col_press); self._tree.bind("<B1-Motion>", self._on_col_motion)

        exc_frame = tk.Frame(self._nb, bg=BG2); self._nb.add(exc_frame, text=f"  {self._t('tab_exceptions')}  ")
        exc_hdr = tk.Frame(exc_frame, bg=BG3); exc_hdr.pack(fill="x")
        self._lbl_exc_count = tk.Label(exc_hdr, text="—", bg=BG3, fg=FG_DIM, font=FONT_UI, padx=12, pady=5); self._lbl_exc_count.pack(side="right")
        tk.Frame(exc_frame, bg=BORDER, height=1).pack(fill="x")
        exc_tree_f = tk.Frame(exc_frame, bg=BG2); exc_tree_f.pack(fill="both", expand=True)
        self._exc_tree = ttk.Treeview(exc_tree_f, columns=cols, show="headings", selectmode="extended")
        exc_vsb = ttk.Scrollbar(exc_tree_f, orient="vertical", command=self._exc_tree.yview); exc_hsb = ttk.Scrollbar(exc_tree_f, orient="horizontal", command=self._exc_tree.xview)
        self._exc_tree.configure(yscrollcommand=exc_vsb.set, xscrollcommand=exc_hsb.set); exc_vsb.pack(side="right", fill="y"); exc_hsb.pack(side="bottom", fill="x"); self._exc_tree.pack(fill="both", expand=True)
        for cid, hkey, width, stretch in col_cfg:
            self._exc_tree.heading(cid, text=self._t(hkey)); self._exc_tree.column(cid, width=width, stretch=tk.YES if stretch else tk.NO, anchor="w")
        self._exc_tree.configure(displaycolumns=self._col_order)
        self._exc_tree.tag_configure("exc_e", background="#16102A", foreground=EXC_CLR); self._exc_tree.tag_configure("exc_o", background="#120E22", foreground=EXC_CLR)
        self._exc_tree.tag_configure("no_exc", background=BG2, foreground=FG_MUT); self._exc_tree.tag_configure("hover", font=(*FONT_CODE[:2], "bold"))
        self._exc_tree.bind("<Double-1>", self._on_exc_double_click); self._exc_tree.bind("<Motion>", self._on_exc_hover); self._exc_tree.bind("<Leave>", self._on_exc_leave)
        self._exc_tree.bind("<ButtonPress-1>", self._on_col_press); self._exc_tree.bind("<B1-Motion>", self._on_col_motion)

        act_bar = tk.Frame(content, bg=BG3); act_bar.pack(fill="x")
        tk.Frame(act_bar, bg=BORDER, height=1).pack(fill="x", side="top")
        inner = tk.Frame(act_bar, bg=BG3); inner.pack(fill="x", padx=12, pady=6)
        self._btn_view = _ab(inner, self._t("view_wwise"), self._view_in_wwise, preset="ghost", font=FONT_UI, padx=14); self._btn_view.pack(side="left", padx=(0, 6))
        self._btn_export = _ab(inner, self._t("export_csv"), self._export_csv, preset="ghost", font=FONT_UI, padx=14); self._btn_export.pack(side="left", padx=(0, 14))
        tk.Frame(inner, bg=BORDER2, width=1).pack(side="left", fill="y", padx=(0, 14), pady=4)
        self._btn_add_exc = _ab(inner, self._t("add_exception"), self._add_exception, preset="exc", font=FONT_UI, padx=14); self._btn_add_exc.pack(side="left", padx=(0, 6))
        self._btn_rem_exc = _ab(inner, self._t("remove_exception"), self._remove_exception, preset="warn", font=FONT_UI, padx=14); self._btn_rem_exc.pack(side="left")

    def _on_col_press(self, event):
        tree = event.widget
        if tree.identify_region(event.x, event.y) != "heading": self._col_drag_id = None; return
        col_num = tree.identify_column(event.x)
        if not col_num or col_num == "#0": self._col_drag_id = None; return
        idx = int(col_num[1:]) - 1
        if 0 <= idx < len(self._col_order): self._col_drag_id = self._col_order[idx]; self._col_drag_x = event.x; self._col_dragging = False

    def _on_col_motion(self, event):
        if not self._col_drag_id: return
        if abs(event.x - self._col_drag_x) < 8: return
        self._col_dragging = True; tree = event.widget; col_num = tree.identify_column(event.x)
        if not col_num or col_num == "#0": return
        tgt_idx = int(col_num[1:]) - 1
        if tgt_idx < 0 or tgt_idx >= len(self._col_order): return
        try: src_idx = self._col_order.index(self._col_drag_id)
        except: return
        if src_idx == tgt_idx: return
        self._col_order.insert(tgt_idx, self._col_order.pop(src_idx))
        self._tree.configure(displaycolumns=self._col_order); self._exc_tree.configure(displaycolumns=self._col_order)

    @staticmethod
    def _effective_type(obj):
        t = obj.get("type", "")
        if t == "WorkUnit":
            fp = obj.get("filePath", "") or ""
            if not fp.lower().endswith(".wwu"): return "PhysicalFolder"
        return t

    def _load_scope_tree(self):
        if not self.client: return
        self.root.after(0, self._clear_scope_tree_loading)
        try:
            r = self.client.call("ak.wwise.core.object.get", {"from":{"path":["\\Actor-Mixer Hierarchy"]}, "transform":[{"select":["children"]}], "options":{"return":["id","name","path","type","filePath"]}})
            children = (r or {}).get("return", [])
        except: return
        def _populate():
            for iid in self._scope_tree.get_children(""): self._scope_tree.delete(iid)
            self._scope_node_paths.clear(); self._scope_node_loaded.clear()
            if not children: self._scope_tree.insert("", "end", text=f"  {self._t('scope_empty')}", tags=("dim",)); return
            root_img = self._type_icon("Folder"); root_label = self._t("scope_root_lbl"); root_iid = self._scope_tree.insert("", "end", text=f" {root_label}" if root_img else f"  ▼ {root_label}", image=root_img or "", open=True)
            self._scope_node_paths[root_iid] = "\\Actor-Mixer Hierarchy"; self._scope_node_loaded[root_iid] = True
            for obj in children:
                eff_t = self._effective_type(obj)
                if eff_t not in SCOPE_TREE_TYPES: continue
                img = self._type_icon(eff_t); text = f" {obj['name']}" if img else f"  {_ICON_FALLBACK.get(eff_t, '○')} {obj['name']}"
                iid = self._scope_tree.insert(root_iid, "end", text=text, image=img or ""); self._scope_node_paths[iid] = obj["path"]; self._scope_node_loaded[iid] = False
                self._scope_tree.insert(iid, "end", iid=iid + _DUMMY_SUFFIX, text="  ...", tags=("dim",))
            self._update_scope_label()
        self.root.after(0, _populate)

    def _clear_scope_tree_loading(self):
        for iid in self._scope_tree.get_children(""): self._scope_tree.delete(iid)
        self._scope_node_paths.clear(); self._scope_node_loaded.clear(); self._scope_tree.insert("", "end", text=f"  {self._t('scope_loading')}", tags=("dim",))

    def _on_scope_expand(self, event):
        iid = self._scope_tree.focus()
        if not iid or self._scope_node_loaded.get(iid, True): return
        wwise_path = self._scope_node_paths.get(iid)
        if not wwise_path: return
        self._scope_node_loaded[iid] = True; threading.Thread(target=self._expand_scope_node, args=(iid, wwise_path), daemon=True).start()

    def _expand_scope_node(self, iid, wwise_path):
        try:
            r = self.client.call("ak.wwise.core.object.get", {"from":{"path":[wwise_path]}, "transform":[{"select":["children"]}], "options":{"return":["id","name","path","type","filePath"]}})
            children = (r or {}).get("return", [])
        except: return
        def _insert():
            dummy = iid + _DUMMY_SUFFIX
            if self._scope_tree.exists(dummy): self._scope_tree.delete(dummy)
            for obj in [c for c in children if self._effective_type(c) in SCOPE_TREE_TYPES]:
                eff_t = self._effective_type(obj); img = self._type_icon(eff_t); text = f" {obj['name']}" if img else f"  {_ICON_FALLBACK.get(eff_t, '○')} {obj['name']}"
                child_iid = self._scope_tree.insert(iid, "end", text=text, image=img or ""); self._scope_node_paths[child_iid] = obj["path"]; self._scope_node_loaded[child_iid] = False
                self._scope_tree.insert(child_iid, "end", iid=child_iid + _DUMMY_SUFFIX, text="  ...", tags=("dim",))
        self.root.after(0, _insert)

    def _on_scope_select(self, event): self._update_scope_label()
    def _update_scope_label(self):
        real_sel = [s for s in self._scope_tree.selection() if s in self._scope_node_paths]
        sel_paths = {self._scope_node_paths[s] for s in real_sel}
        if (not real_sel) or sel_paths == {"\\Actor-Mixer Hierarchy"}: self._lbl_scope_sel.config(text=self._t("scope_all_lbl"), fg=FG_MUT)
        else: self._lbl_scope_sel.config(text=self._t("scope_sel_lbl").format(len(real_sel)), fg=ACCENT)

    def _get_scope_paths(self):
        paths = {self._scope_node_paths[s] for s in self._scope_tree.selection() if s in self._scope_node_paths}
        return set() if paths == {"\\Actor-Mixer Hierarchy"} else paths

    def _matches_scope(self, path, scope_paths):
        if not scope_paths: return True
        return any(path == sp or path.startswith(sp + "\\") for sp in scope_paths)

    def _load_exceptions(self):
        try:
            if os.path.exists(EXCEPTIONS_FILE):
                with open(EXCEPTIONS_FILE, "r", encoding="utf-8") as f: self._exceptions = json.load(f)
        except: self._exceptions = {}

    def _save_exceptions(self):
        try:
            with open(EXCEPTIONS_FILE, "w", encoding="utf-8") as f: json.dump(self._exceptions, f, ensure_ascii=False, indent=2)
        except: pass

    def _add_exception(self):
        sel = self._tree.selection()
        if not sel: messagebox.showinfo(self._t("info_title"), self._t("select_to_except"), parent=self.root); return
        to_remove_ids = set()
        for iid in sel:
            idx = self._tree.index(iid)
            if idx >= len(self._results): continue
            r = self._results[idx]; obj_id = r.get("id", "")
            if not obj_id: continue
            self._exceptions[obj_id] = {"name": r["name"], "type": r["type"], "spat": r["spat"], "att": r["att"], "issue": r["issue"], "wu": r["wu"], "path": r["path"], "fp": [r["spat"], r["att"], r["issue"]]}
            to_remove_ids.add(obj_id)
        if to_remove_ids:
            self._results = [r for r in self._results if r.get("id") not in to_remove_ids]; self._save_exceptions(); self._populate_results(); self._populate_exceptions(); self._nb.select(1)

    def _remove_exception(self):
        sel = self._exc_tree.selection()
        if not sel: messagebox.showinfo(self._t("info_title"), self._t("select_to_unexcept"), parent=self.root); return
        for iid in sel:
            idx = self._exc_tree.index(iid)
            if idx < len(self._exc_order): self._exceptions.pop(self._exc_order[idx], None)
        self._save_exceptions(); self._populate_exceptions()

    def _populate_exceptions(self):
        self._exc_tree.delete(*self._exc_tree.get_children()); self._exc_order = []
        if not self._exceptions: self._exc_tree.insert("", "end", values=(f"—  {self._t('no_exceptions')}", "", "", "", "", "", ""), tags=("no_exc",)); self._lbl_exc_count.config(text="—", fg=FG_DIM); return
        exc_list = list(self._exceptions.items()); self._lbl_exc_count.config(text=self._t("exc_count").format(len(exc_list)), fg=EXC_CLR)
        for i, (obj_id, ex) in enumerate(exc_list):
            self._exc_order.append(obj_id); sfx = "e" if i % 2 == 0 else "o"
            self._exc_tree.insert("", "end", values=(ex["name"], ex["type"], ex["spat"], ex["att"], self._t(f"issue_{ex['issue']}"), ex["wu"], ex["path"]), tags=(f"exc_{sfx}",))

    def _on_hover(self, event):
        iid = self._tree.identify_row(event.y)
        if iid == self._hover_iid: return
        if self._hover_iid: self._tree.item(self._hover_iid, tags=[t for t in self._tree.item(self._hover_iid, "tags") if t != "hover"])
        self._hover_iid = iid
        if iid: self._tree.item(iid, tags=list(self._tree.item(iid, "tags")) + ["hover"])

    def _on_leave(self, event):
        if self._hover_iid: self._tree.item(self._hover_iid, tags=[t for t in self._tree.item(self._hover_iid, "tags") if t != "hover"]); self._hover_iid = None

    def _on_exc_hover(self, event):
        iid = self._exc_tree.identify_row(event.y)
        if iid == self._hover_exc_iid: return
        if self._hover_exc_iid: self._exc_tree.item(self._hover_exc_iid, tags=[t for t in self._exc_tree.item(self._hover_exc_iid, "tags") if t != "hover"])
        self._hover_exc_iid = iid
        if iid: self._exc_tree.item(iid, tags=list(self._exc_tree.item(iid, "tags")) + ["hover"])

    def _on_exc_leave(self, event):
        if self._hover_exc_iid: self._exc_tree.item(self._hover_exc_iid, tags=[t for t in self._exc_tree.item(self._hover_exc_iid, "tags") if t != "hover"]); self._hover_exc_iid = None

    def _sort_by(self, col):
        if self._col_dragging: self._col_dragging = False; return
        self._sort_rev = not self._sort_rev if self._sort_col == col else False; self._sort_col = col
        self._results.sort(key=lambda r: (r.get(col) or "").lower(), reverse=self._sort_rev); self._populate_results()

    def _show_help(self):
        dlg = tk.Toplevel(self.root); dlg.title(self._t("help_title")); dlg.configure(bg=BG); dlg.resizable(True, True); dlg.grab_set()
        hdr = tk.Frame(dlg, bg=BG3); hdr.pack(fill="x"); tk.Frame(hdr, bg=ACCENT, height=2).pack(fill="x", side="bottom")
        tk.Label(hdr, text=self._t("help_title"), bg=BG3, fg=FG, font=FONT_H2, anchor="w").pack(padx=16, pady=10)
        body = tk.Frame(dlg, bg=BG); body.pack(fill="both", expand=True, padx=2); vsb = ttk.Scrollbar(body, orient="vertical"); vsb.pack(side="right", fill="y")
        txt = tk.Text(body, bg=BG2, fg=FG, font=FONT_UI, wrap="word", relief="flat", borderwidth=0, padx=16, pady=12, yscrollcommand=vsb.set, cursor="arrow"); txt.pack(fill="both", expand=True); vsb.config(command=txt.yview)
        txt.tag_config("sec", foreground=ACCENT, font=FONT_UIB); txt.tag_config("body", foreground=FG_DIM, font=FONT_UI)
        for line in self._t("help_body").split("\n"): txt.insert("end", line + "\n", "sec" if line.startswith("【") else "body")
        txt.config(state="disabled"); btn_f = tk.Frame(dlg, bg=BG3); btn_f.pack(fill="x"); tk.Frame(btn_f, bg=BORDER, height=1).pack(fill="x", side="top")
        tk.Button(btn_f, text="닫기", command=dlg.destroy, bg=PANEL, fg=FG_DIM, activebackground=BORDER2, activeforeground=FG, relief="flat", font=FONT_UIB, padx=20, pady=6, cursor="hand2").pack(side="right", padx=12, pady=8); dlg.geometry("540x520")

    def _set_status(self, msg, color=FG_DIM, key=None, args=()):
        self._cur_status_key = key; self._cur_status_args = args; self._cur_status_color = color; self._status_lbl.config(text=msg, fg=color); self._status_dot.config(fg=color)

    def _set_proj_name(self, name):
        self._proj_name = name; self._proj_lbl.config(text=name); self._proj_sep.config(text="  ·  " if name else "")

    def _start_wwise_watchdog(self):
        def _watch():
            while True:
                time.sleep(3)
                if not self._was_connected: continue
                try: s = socket.create_connection(("127.0.0.1", 8080), timeout=2); s.close()
                except: self.root.after(0, self.root.destroy); return
        threading.Thread(target=_watch, daemon=True).start()

    def _connect_waapi(self):
        self.root.after(0, lambda: self._set_status(self._t("connecting"), WARN))
        if not WAAPI_AVAILABLE: self.root.after(0, lambda: self._set_status(self._t("no_waapi"), ERR_CLR)); return
        try:
            if self.client:
                try: self.client.disconnect()
                except: pass
            self.client = WaapiClient(url=WAAPI_URL); self._find_cmd = None
            r = self.client.call("ak.wwise.core.object.get", {"from":{"ofType":["Project"]}, "options":{"return":["name"]}})
            proj = (r or {}).get("return", [{}]); proj_name = proj[0].get("name", "—") if proj else "—"
            self._was_connected = True; self.root.after(0, lambda: self._set_proj_name(proj_name))
            self.root.after(0, lambda: self._set_status(self._t("connected"), OK_CLR, key="connected"))
            threading.Thread(target=self._load_scope_tree, daemon=True).start()
        except Exception as e:
            self.client = None; self.root.after(0, lambda: self._set_proj_name(""))
            self.root.after(0, lambda: self._set_status(self._t("connect_fail").format(e), ERR_CLR))

    def _select_in_wwise(self, object_id):
        if not self.client: return
        if self._find_cmd:
            try: self.client.call("ak.wwise.ui.commands.execute", {"command": self._find_cmd, "objects": [object_id]})
            except: self._find_cmd = None
        if not self._find_cmd:
            for cmd in FIND_CMD_PRIMARY:
                try: self.client.call("ak.wwise.ui.commands.execute", {"command": cmd, "objects": [object_id]}); self._find_cmd = cmd; break
                except: continue
            else: self.root.after(0, lambda: messagebox.showwarning(self._t("info_title"), self._t("not_found"), parent=self.root)); return
        try: self.client.call("ak.wwise.ui.commands.execute", {"command": "Inspect", "objects": [object_id]})
        except: pass

    @staticmethod
    def _resolve_effective(path, obj_map, cache):
        chain = []; cur = path
        while True:
            if cur in cache:
                res = cache[cur]
                for p in chain: cache[p] = res
                return res
            obj = obj_map.get(cur)
            if obj:
                ovr = obj.get("@OverridePositioning")
                if ovr is True or (ovr is None and "@ListenerRelativeRouting" in obj):
                    for p in chain + [cur]: cache[p] = obj
                    return obj
            chain.append(cur); sep = cur.rfind("\\")
            if sep <= 0: break
            cur = cur[:sep]
        for p in chain: cache[p] = None
        return None

    def _run_scan(self):
        if not self.client: messagebox.showerror(self._t("error_title"), self._t("no_wwise"), parent=self.root); return
        if not self._opt_sounds.get() and not self._opt_containers.get(): messagebox.showwarning(self._t("info_title"), self._t("no_type"), parent=self.root); return
        self._set_status(self._t("scanning"), WARN); self._btn_scan.config(state="disabled")
        scope_paths = self._get_scope_paths()
        def worker():
            try:
                r = self.client.call("ak.wwise.core.object.get", {"from":{"ofType":["Sound", "ActorMixer", "RandomSequenceContainer", "BlendContainer", "SwitchContainer", "Folder", "WorkUnit"]}, "options":{"return":["id", "name", "path", "type", "workunit", "@OverridePositioning", "@ListenerRelativeRouting", "@3DSpatialization", "@Attenuation", "@EnableAttenuation"]}})
                all_objs = (r or {}).get("return", []); obj_map = {o["path"]: o for o in all_objs}; eff_cache = {}; audit_types = set()
                if self._opt_sounds.get(): audit_types.add("Sound")
                if self._opt_containers.get(): audit_types.update(CONTAINER_TYPES)
                results = []; _SPAT_LABEL = {0: "None", 1: "Position", 2: "Position + Orientation"}; invalidated = []
                for obj in all_objs:
                    if obj.get("type") not in audit_types or not self._matches_scope(obj.get("path", ""), scope_paths): continue
                    eff = self._resolve_effective(obj["path"], obj_map, eff_cache)
                    if eff is None: continue
                    lr = eff.get("@ListenerRelativeRouting", False); spat = eff.get("@3DSpatialization", 0); is_3d = bool(lr) and spat != 0
                    att_ref = eff.get("@Attenuation") or {}; att_name = att_ref.get("name", "") if isinstance(att_ref, dict) else ""; att_enable = eff.get("@EnableAttenuation", False); att_active = bool(att_enable) and bool(att_name)
                    if is_3d and not att_active: issue = "miss"
                    elif not is_3d and att_active: issue = "extra"
                    else: continue
                    att_label = att_name if att_name else "—"
                    if att_name and not att_enable: att_label += "  (disabled)"
                    spat_label = _SPAT_LABEL.get(spat, str(spat)); obj_id = obj.get("id", ""); fp = [spat_label, att_label, issue]
                    if obj_id in self._exceptions:
                        if fp == self._exceptions[obj_id].get("fp", []): continue
                        else: invalidated.append(obj_id); del self._exceptions[obj_id]
                    wu = obj.get("workunit") or {}; wu_name = wu.get("name", "") if isinstance(wu, dict) else ""
                    results.append({"id": obj_id, "name": obj.get("name", ""), "type": obj.get("type", ""), "spat": spat_label, "att": att_label, "issue": issue, "wu": wu_name, "path": obj["path"]})
                if invalidated: self._save_exceptions()
                self._results = results; self._total_checked = sum(1 for o in all_objs if o.get("type") in audit_types and self._matches_scope(o.get("path", ""), scope_paths)); self._scanned = True
                _c = ERR_CLR if results else OK_CLR
                self.root.after(0, self._populate_results); self.root.after(0, self._populate_exceptions)
                self.root.after(0, lambda c=_c, t=self._total_checked, v=len(results): self._set_status(self._t("scan_done").format(t, v), c, key="scan_done", args=(t, v)))
                self.root.after(0, lambda: self._nb.select(0))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(self._t("error_title"), self._t("scan_fail").format(e), parent=self.root))
                self.root.after(0, lambda: self._set_status(self._t("scan_fail").format(e), ERR_CLR))
            finally: self.root.after(0, lambda: self._btn_scan.config(state="normal"))
        threading.Thread(target=worker, daemon=True).start()

    def _populate_results(self):
        self._tree.delete(*self._tree.get_children())
        if not self._results:
            if self._scanned:
                msg = self._t("no_violations").format(self._total_checked); self._tree.insert("", "end", values=(f"✓  {msg}", "", "", "", "", "", ""), tags=("ok_msg",)); self._lbl_count.config(text=msg, fg=OK_CLR)
            else: self._lbl_count.config(text="—", fg=FG_DIM)
            return
        self._lbl_count.config(text=self._t("violations_fmt").format(len(self._results)), fg=ERR_CLR)
        for i, r in enumerate(self._results):
            sfx = "e" if i % 2 == 0 else "o"; self._tree.insert("", "end", values=(r["name"], r["type"], r["spat"], r["att"], self._t(f"issue_{r['issue']}"), r["wu"], r["path"]), tags=(f"{r['issue']}_{sfx}",))

    def _on_double_click(self, event):
        iid = self._tree.identify_row(event.y)
        if not iid: return
        idx = self._tree.index(iid)
        if idx < len(self._results):
            obj_id = self._results[idx].get("id", ""); threading.Thread(target=self._select_in_wwise, args=(obj_id,), daemon=True).start()

    def _on_exc_double_click(self, event):
        iid = self._exc_tree.identify_row(event.y)
        if not iid: return
        idx = self._exc_tree.index(iid)
        if idx < len(self._exc_order):
            obj_id = self._exc_order[idx]; threading.Thread(target=self._select_in_wwise, args=(obj_id,), daemon=True).start()

    def _view_in_wwise(self):
        if self._nb.index("current") == 0:
            sel = self._tree.selection()
            if not sel: messagebox.showinfo(self._t("info_title"), self._t("select_item"), parent=self.root); return
            idx = self._tree.index(sel[0]); obj_id = self._results[idx].get("id", ""); threading.Thread(target=self._select_in_wwise, args=(obj_id,), daemon=True).start()
        else:
            sel = self._exc_tree.selection()
            if not sel: messagebox.showinfo(self._t("info_title"), self._t("select_item"), parent=self.root); return
            idx = self._exc_tree.index(sel[0]); obj_id = self._exc_order[idx]; threading.Thread(target=self._select_in_wwise, args=(obj_id,), daemon=True).start()

    def _export_csv(self):
        if not self._results: messagebox.showinfo(self._t("info_title"), self._t("no_results"), parent=self.root); return
        path = filedialog.asksaveasfilename(title=self._t("csv_title"), defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("All", "*.*")], parent=self.root)
        if not path: return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow([self._t(k) for k in ("col_name", "col_type", "col_3d", "col_att", "col_issue", "col_wu", "col_path")])
            for r in self._results: w.writerow([r["name"], r["type"], r["spat"], r["att"], self._t(f"issue_{r['issue']}"), r["wu"], r["path"]])
        messagebox.showinfo(self._t("info_title"), self._t("csv_done").format(path), parent=self.root)


if __name__ == "__main__":
    import ctypes; hwnd = ctypes.windll.user32.FindWindowW(None, "Attenuation Auditor  —  Wwise")
    if hwnd: ctypes.windll.user32.ShowWindow(hwnd, 9); ctypes.windll.user32.SetForegroundWindow(hwnd)
    else: root = tk.Tk(); AttenuationAuditor(root); root.mainloop()
