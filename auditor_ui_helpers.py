import tkinter as tk

from auditor_constants import FG_MUT, FONT_UIB


# ── Animated button ───────────────────────────────────────────────────────────
def _ab(parent, text, cmd=None, preset="ghost", font=None, padx=14, **kw):
    from auditor_constants import _BP
    bg, fg, hov, prs = _BP[preset]
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg, relief="flat", bd=0,
                  font=font or FONT_UIB, padx=padx, pady=6,
                  cursor="hand2", disabledforeground=FG_MUT,
                  activebackground=hov, activeforeground=fg, **kw)
    def _enter(e):
        if str(b.cget("state")) != "disabled": b.config(bg=hov)
    def _leave(e): b.config(bg=bg)
    def _press(e):
        if str(b.cget("state")) != "disabled": b.config(bg=prs)
    def _release(e):
        if str(b.cget("state")) != "disabled": b.config(bg=hov)
    b.bind("<Enter>",           _enter)
    b.bind("<Leave>",           _leave)
    b.bind("<Button-1>",        _press)
    b.bind("<ButtonRelease-1>", _release)
    return b
