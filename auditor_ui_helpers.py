import tkinter as tk

from auditor_constants import BORDER2, FG_MUT, FONT_UIB


# ── Animated button ───────────────────────────────────────────────────────────
def _ab(parent, text, cmd=None, preset="ghost", font=None, padx=14, **kw):
    from auditor_constants import _BP
    bg, fg, hov, prs = _BP[preset]
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg, relief="flat", bd=0,
                  font=font or FONT_UIB, padx=padx, pady=5,
                  cursor="hand2", disabledforeground=FG_MUT,
                  highlightthickness=1, highlightbackground=bg,
                  highlightcolor=BORDER2, takefocus=True,
                  activebackground=hov, activeforeground=fg, **kw)
    def _enter(e):
        if str(b.cget("state")) != "disabled": b.config(bg=hov, highlightbackground=BORDER2)
    def _leave(e): b.config(bg=bg, highlightbackground=bg)
    def _press(e):
        if str(b.cget("state")) != "disabled": b.config(bg=prs)
    def _release(e):
        if str(b.cget("state")) != "disabled": b.config(bg=hov, highlightbackground=BORDER2)
    def _focus_in(e): b.config(highlightbackground=BORDER2)
    def _focus_out(e): b.config(highlightbackground=bg)
    b.bind("<Enter>",           _enter)
    b.bind("<Leave>",           _leave)
    b.bind("<Button-1>",        _press)
    b.bind("<ButtonRelease-1>", _release)
    b.bind("<FocusIn>",         _focus_in)
    b.bind("<FocusOut>",        _focus_out)
    return b
