"""
main.py
=======
Image Processing Studio — aplikasi desktop pengolahan citra digital (PCD).
Didesain dengan UI Modern, Sleek Dark Navy Fluent Theme, dan Tipografi Mutakhir.

Tim Pengembang : Visionary
Anggota Tim    :
  1. Azwa Zahira                (2407126204)
  2. Bulan Hijarati Asy-Syiddah (2407134878)
  3. Nur Diana Tri Zahara       (2407111549)
Mata Kuliah    : Pengolahan Citra Digital (PCD)
Tanggal Update : 24/11/2026
Hak Cipta      : Copyright © 2026 Visionary - All Rights Reserved
"""
from __future__ import annotations

import ctypes
import os
import sys
import tkinter as tk
from tkinter import filedialog, font, messagebox, ttk
from typing import Callable, Dict, List, Optional, Tuple, Union
import webbrowser

from PIL import Image, ImageTk
import numpy as np

import histogram as hist
import operations as ops

APP_NAME = "Image Processing Studio - Copyright © Visionary (2026)"
TEAM_NAME = "Visionary"
UPDATE_DATE = "24/11/2026"
COPYRIGHT_TEXT = "Copyright © 2026 Visionary - All Rights Reserved"

# Anggota Tim Visionary
TEAM_MEMBERS = [
    ("Azwa Zahira", "2407126204"),
    ("Bulan Hijarati Asy-Syiddah", "2407134878"),
    ("Nur Diana Tri Zahara", "2407111549"),
]

# --------------------------------------------------------------------------
# Palet Warna Modern (Sleek Obsidian Navy & Electric Indigo/Blue)
# --------------------------------------------------------------------------
C = {
    "bg": "#0b0f19",           # Latar belakang utama (deep space obsidian)
    "sidebar": "#101728",      # Sidebar navigasi
    "panel": "#141e34",        # Panel pratinjau & modal
    "card": "#182440",         # Kartu informasi
    "card_border": "#27375e",  # Border kartu
    "input": "#0c1322",        # Latar input & canvas citra
    "border": "#223154",       # Border umum
    "border_light": "#2e4170", # Border aksen lembut
    "accent": "#3b82f6",       # Electric blue aksen utama
    "accent_h": "#60a5fa",     # Hover aksen biru
    "accent_glow": "#93c5fd",  # Glow teks aksen
    "purple": "#8b5cf6",       # Aksen sekunder ungu/indigo
    "purple_h": "#a78bfa",     # Hover ungu
    "text": "#f8fafc",         # Teks utama (high contrast)
    "text_sub": "#cbd5e1",     # Teks sekunder
    "muted": "#94a3b8",        # Teks pudar / label
    "dim": "#64748b",          # Teks placeholder / garis
    "btn": "#17233f",          # Background tombol default
    "btn_h": "#22335c",        # Hover tombol default
    "danger": "#f43f5e",       # Merah aksen bahaya / keluar
    "danger_h": "#e11d48",     # Hover bahaya
    "ok": "#10b981",           # Emerald green (sukses / aktif)
    "warn": "#f59e0b",         # Amber warning
}

OPEN_TYPES = [
    ("Semua gambar", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp *.gif"),
    ("PNG", "*.png"),
    ("JPEG", "*.jpg *.jpeg"),
    ("BMP", "*.bmp"),
    ("TIFF", "*.tif *.tiff"),
    ("WEBP", "*.webp"),
    ("Semua file", "*.*"),
]
SAVE_TYPES = [
    ("PNG", "*.png"),
    ("JPEG", "*.jpg *.jpeg"),
    ("BMP", "*.bmp"),
    ("TIFF", "*.tif *.tiff"),
    ("WEBP", "*.webp"),
]
SAVE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
FORMAT_EXT = {"PNG": ".png", "JPEG": ".jpg", "BMP": ".bmp", "TIFF": ".tif", "WEBP": ".webp"}


def _enable_dpi_awareness() -> None:
    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def _resolve_fonts() -> Tuple[str, str, str]:
    """Deteksi font terbaik yang terpasang di sistem (Windows 11/10 Fluent font)."""
    try:
        dummy = tk.Tk()
        dummy.withdraw()
        fams = set(font.families(dummy))
        dummy.destroy()
    except Exception:
        fams = set()

    # Font teks body & tombol
    if "Segoe UI Variable Text" in fams:
        f_main = "Segoe UI Variable Text"
    elif "Segoe UI" in fams:
        f_main = "Segoe UI"
    elif "Aptos" in fams:
        f_main = "Aptos"
    else:
        f_main = "Helvetica"

    # Font judul display
    if "Segoe UI Variable Display" in fams:
        f_disp = "Segoe UI Variable Display"
    elif "Segoe UI" in fams:
        f_disp = "Segoe UI"
    else:
        f_disp = f_main

    # Font monospace
    f_mono = "Consolas" if "Consolas" in fams else "Courier New"
    return f_main, f_disp, f_mono


FONT, FONT_DISPLAY, FONT_MONO = _resolve_fonts()


# ==========================================================================
# Widget Kustom dengan Styling Modern
# ==========================================================================
class HoverButton(tk.Button):
    """Tombol modern dengan feedback visual hover dan active state."""

    STYLES = {
        "side": ("btn", "btn_h", "text", "border"),
        "accent": ("accent", "accent_h", "#ffffff", "accent"),
        "purple": ("purple", "purple_h", "#ffffff", "purple"),
        "ghost": ("card", "btn_h", "text_sub", "border"),
        "danger": ("btn", "#4c1322", "danger", "border"),
    }

    def __init__(self, parent, text: str, command: Callable, style: str = "side", **kw):
        bg, hover, fg, bdr = self.STYLES.get(style, self.STYLES["side"])
        self._bg = C.get(bg, bg)
        self._hover = C.get(hover, hover)
        self._bdr = C.get(bdr, bdr)
        fg_col = C.get(fg, fg)

        opts = dict(
            text=text, command=command, bg=self._bg, fg=fg_col,
            activebackground=self._hover, activeforeground=fg_col,
            relief="flat", bd=0, cursor="hand2", font=(FONT, 10, "bold" if style in ("accent", "purple") else "normal"),
            highlightthickness=1, highlightbackground=self._bdr, highlightcolor=C["accent"],
            padx=12, pady=6,
        )
        opts.update(kw)
        super().__init__(parent, **opts)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e=None):
        self.configure(bg=self._hover, highlightbackground=C["accent"])

    def _on_leave(self, _e=None):
        self.configure(bg=self._bg, highlightbackground=self._bdr)


class ScrollFrame(tk.Frame):
    """Frame sidebar scrollable dengan scrollbar halus."""

    def __init__(self, parent, bg: str, width: int):
        super().__init__(parent, bg=bg, width=width)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, width=width)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        self.bind("<Enter>", self._bind_wheel)
        self.bind("<Leave>", self._unbind_wheel)

    def _on_inner(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        need_scroll = self.inner.winfo_reqheight() > self.canvas.winfo_height()
        if need_scroll:
            self.vsb.pack(side="right", fill="y")
        else:
            self.vsb.pack_forget()

    def _bind_wheel(self, _e=None):
        self.canvas.bind_all("<MouseWheel>", self._wheel)
        self.canvas.bind_all("<Button-4>", self._wheel)
        self.canvas.bind_all("<Button-5>", self._wheel)

    def _unbind_wheel(self, _e=None):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.unbind_all(seq)

    def _wheel(self, event):
        if self.inner.winfo_reqheight() <= self.canvas.winfo_height():
            return
        if getattr(event, "num", None) == 4:
            step = -1
        elif getattr(event, "num", None) == 5:
            step = 1
        else:
            step = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(step * 2, "units")


class ImagePanel(tk.Frame):
    """Panel pratinjau citra yang modern dengan status dot dan border aksen."""

    MAX_UPSCALE = 4.0

    def __init__(self, parent, title: str, placeholder: str, dot_color: str = "#38bdf8"):
        super().__init__(parent, bg=C["panel"], highlightthickness=1, highlightbackground=C["border"])
        head = tk.Frame(self, bg=C["panel"])
        head.pack(fill="x", padx=14, pady=(10, 2))
        self.dot = tk.Label(head, text="●", bg=C["panel"], fg=dot_color, font=(FONT, 10))
        self.dot.pack(side="left")
        self.title_lbl = tk.Label(head, text=title, bg=C["panel"], fg=C["text"], font=(FONT_DISPLAY, 12, "bold"))
        self.title_lbl.pack(side="left", padx=6)

        self.canvas = tk.Canvas(self, bg=C["input"], highlightthickness=1, highlightbackground=C["border"])
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(8, 12))
        self.placeholder = placeholder
        self.image: Optional[Image.Image] = None
        self._photo = None
        self._after = None
        self.canvas.bind("<Configure>", lambda e: self._schedule())

    def set_image(self, img: Optional[Image.Image]) -> None:
        self.image = img
        self._draw()

    def _schedule(self) -> None:
        if self._after is None:
            self._after = self.after(30, self._draw)

    def _draw(self) -> None:
        self._after = None
        c = self.canvas
        c.delete("all")
        cw, ch = c.winfo_width(), c.winfo_height()
        if cw < 20 or ch < 20:
            return
        if self.image is None:
            c.create_text(
                cw / 2, ch / 2, text=self.placeholder, fill=C["muted"],
                font=(FONT, 11), justify="center",
            )
            return
        iw, ih = self.image.size
        scale = min((cw - 24) / iw, (ch - 24) / ih, self.MAX_UPSCALE)
        nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
        if (nw, nh) == (iw, ih):
            shown = self.image
        elif scale < 1:
            shown = self.image.resize((nw, nh), ops.BILINEAR, reducing_gap=2.0)
        else:
            shown = self.image.resize((nw, nh), ops.BICUBIC)
        self._photo = ImageTk.PhotoImage(shown)
        x0, y0 = (cw - nw) // 2, (ch - nh) // 2
        c.create_rectangle(x0 - 1, y0 - 1, x0 + nw, y0 + nh, outline=C["border_light"])
        c.create_image(x0, y0, image=self._photo, anchor="nw")

        # Badge info resolusi di sudut kanan bawah canvas
        c.create_rectangle(cw - 195, ch - 28, cw - 6, ch - 6, fill=C["sidebar"], outline=C["border"])
        c.create_text(
            cw - 100, ch - 17, fill=C["text_sub"], font=(FONT_MONO, 9),
            text=f"{iw}×{ih}px • {int(scale * 100)}%",
        )


class InfoCard(tk.Frame):
    """Kartu metadata citra dengan layout rapi dan aksen header."""

    def __init__(self, parent, title: str, rows: List[tuple], accent_color: str = "#60a5fa"):
        super().__init__(parent, bg=C["card"], highlightthickness=1, highlightbackground=C["card_border"])
        head = tk.Frame(self, bg=C["card"])
        head.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 6))
        tk.Label(head, text="✦", bg=C["card"], fg=accent_color, font=(FONT, 9)).pack(side="left")
        tk.Label(head, text=f" {title}", bg=C["card"], fg=accent_color, font=(FONT_DISPLAY, 10, "bold")).pack(side="left")

        self.vars: Dict[str, tk.StringVar] = {}
        for i, (key, label) in enumerate(rows, start=1):
            tk.Label(self, text=label, bg=C["card"], fg=C["muted"], font=(FONT, 10)).grid(
                row=i, column=0, sticky="nw", padx=(14, 12), pady=2)
            var = tk.StringVar(value="-")
            tk.Label(self, textvariable=var, bg=C["card"], fg=C["text"], font=(FONT, 10),
                     anchor="w", justify="left", wraplength=340).grid(row=i, column=1, sticky="w", pady=2)
            self.vars[key] = var
        tk.Frame(self, bg=C["card"], height=10).grid(row=len(rows) + 1, column=0)
        self.grid_columnconfigure(1, weight=1)

    def update_info(self, data: Dict[str, str]) -> None:
        for key, var in self.vars.items():
            var.set(data.get(key, "-"))


def _make_entry(parent, var, width=10):
    return tk.Entry(
        parent, textvariable=var, width=width, bg=C["input"], fg=C["text"],
        insertbackground=C["accent_h"], relief="flat", font=(FONT_MONO, 11),
        highlightthickness=1, highlightbackground=C["border"], highlightcolor=C["accent"],
    )


# ==========================================================================
# Dialog Dasar & Dialog Parameter
# ==========================================================================
class BaseDialog(tk.Toplevel):
    """Dialog modal bertema modern dark navy."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.withdraw()
        self.title(title)
        self.configure(bg=C["panel"])
        self.transient(parent)
        self.resizable(False, False)
        self.result = None
        self._parent = parent
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda e: self._cancel())

    def _label(self, parent, text, muted=False, **kw):
        return tk.Label(parent, text=text, bg=C["panel"], fg=C["muted" if muted else "text"],
                        font=(FONT, 10.5), **kw)

    def _buttons(self, ok_text="Terapkan", extra: Optional[List[tuple]] = None):
        row = tk.Frame(self, bg=C["panel"])
        row.pack(fill="x", padx=22, pady=(10, 18))
        for text, cmd in (extra or []):
            HoverButton(row, text, cmd, style="ghost", padx=12, pady=5).pack(side="left", padx=(0, 6))
        HoverButton(row, ok_text, self._ok, style="accent", padx=18, pady=5).pack(side="right")
        HoverButton(row, "Batal", self._cancel, style="ghost", padx=14, pady=5).pack(side="right", padx=6)
        self.bind("<Return>", lambda e: self._ok())

    def _ok(self):
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        self.update_idletasks()
        p = self._parent.winfo_toplevel()
        x = p.winfo_rootx() + (p.winfo_width() - self.winfo_reqwidth()) // 2
        y = p.winfo_rooty() + (p.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.deiconify()
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_set()
        self.wait_window(self)
        return self.result


class SliderDialog(BaseDialog):
    """Dialog dengan slider parameter interaktif dan live preview."""

    def __init__(self, parent, title: str, fields: List[dict], preview: Callable[[dict], None],
                 presets: Optional[List[tuple]] = None, hint: str = ""):
        super().__init__(parent, title)
        self.fields = fields
        self.preview = preview
        self.scales: Dict[str, ttk.Scale] = {}
        self._vars: Dict[str, tk.DoubleVar] = {}
        self._value_labels: Dict[str, tk.Label] = {}
        self._job = None

        body = tk.Frame(self, bg=C["panel"])
        body.pack(padx=24, pady=(18, 6), fill="x")
        if hint:
            self._label(body, hint, muted=True, justify="left", wraplength=350).pack(anchor="w", pady=(0, 8))
        for f in fields:
            row = tk.Frame(body, bg=C["panel"])
            row.pack(fill="x", pady=(10, 0))
            self._label(row, f["label"], font=(FONT, 10.5)).pack(side="left")
            value_label = tk.Label(row, bg=C["panel"], fg=C["accent_h"], font=(FONT_MONO, 11, "bold"))
            value_label.pack(side="right")
            var = tk.DoubleVar(value=f["default"])
            sc = ttk.Scale(body, from_=f["min"], to=f["max"], orient="horizontal", length=350,
                           variable=var, style="Studio.Horizontal.TScale")
            sc.pack(fill="x", pady=(4, 0))
            self.scales[f["key"]] = sc
            self._vars[f["key"]] = var
            self._value_labels[f["key"]] = value_label
        self._update_labels()
        for var in self._vars.values():
            var.trace_add("write", lambda *a: self._changed())

        extra = [("Reset", self._reset)]
        for text, vals in (presets or []):
            extra.append((text, lambda v=vals: self._apply_preset(v)))
        self._buttons(extra=extra)
        self.after(60, self._fire)

    @staticmethod
    def _snap(f: dict, raw: float):
        step = float(f.get("step", 1))
        value = min(max(round(raw / step) * step, f["min"]), f["max"])
        return int(round(value)) if step.is_integer() else round(value, 4)

    def values(self) -> dict:
        return {f["key"]: self._snap(f, float(self._vars[f["key"]].get())) for f in self.fields}

    def _update_labels(self) -> None:
        for f in self.fields:
            val = self.values()[f["key"]]
            step = float(f.get("step", 1))
            txt = f"{val}" if step.is_integer() else f"{val:.2f}"
            self._value_labels[f["key"]].configure(text=txt)

    def _changed(self) -> None:
        self._update_labels()
        if self._job is not None:
            self.after_cancel(self._job)
        self._job = self.after(80, self._fire)

    def _fire(self) -> None:
        self._job = None
        try:
            self.preview(self.values())
        except Exception:
            pass

    def _reset(self) -> None:
        for f in self.fields:
            self.scales[f["key"]].set(f["default"])
        self._changed()

    def _apply_preset(self, vals: dict) -> None:
        for k, v in vals.items():
            if k in self.scales:
                self.scales[k].set(v)
        self._changed()

    def _close_jobs(self) -> None:
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None

    def _ok(self):
        self._close_jobs()
        self.result = self.values()
        self.destroy()

    def _cancel(self):
        self._close_jobs()
        super()._cancel()


class ConvolutionDialog(BaseDialog):
    """Dialog Konvolusi dengan Matriks 3×3 Interaktif & Preset Soal Halaman 2 (1-8-0)."""

    PRESETS = [
        ("Template Soal (1,2,3 / 4,5,6 / 7,8,0)",
         [[1, 2, 3], [4, 5, 6], [7, 8, 0]], None, 0),
        ("Gaussian Blur (1,2,1 / 2,4,2 / 1,2,1)",
         [[1, 2, 1], [2, 4, 2], [1, 2, 1]], 16.0, 0),
        ("Box Blur (Mean Rata-rata)",
         [[1, 1, 1], [1, 1, 1], [1, 1, 1]], 9.0, 0),
        ("Sharpen (Pertajam)",
         [[0, -1, 0], [-1, 5, -1], [0, -1, 0]], 1.0, 0),
        ("Highpass Filter",
         [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], 1.0, 0),
        ("Laplacian Edge",
         [[0, 1, 0], [1, -4, 1], [0, 1, 0]], 1.0, 128),
        ("Sobel Horisontal",
         [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], 1.0, 128),
        ("Sobel Vertikal",
         [[-1, -2, -1], [0, 0, 0], [1, 2, 1]], 1.0, 128),
        ("Emboss",
         [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]], 1.0, 128),
        ("Identitas",
         [[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1.0, 0),
    ]

    def __init__(self, parent, preview: Callable[[np.ndarray, Optional[float], float], None]):
        super().__init__(parent, "Konvolusi Citra (Kernel 3×3)")
        self.preview = preview

        body = tk.Frame(self, bg=C["panel"])
        body.pack(padx=24, pady=(18, 6))

        self._label(body, "Matriks Kernel Konvolusi 3×3:", font=(FONT_DISPLAY, 10, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        defaults = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        self.entries = []
        for r in range(3):
            row_entries = []
            for col in range(3):
                var = tk.StringVar(value=str(defaults[r][col]))
                e = _make_entry(body, var, width=7)
                e.grid(row=r + 1, column=col, padx=4, pady=4, ipady=4)
                var.trace_add("write", lambda *a: self._on_change())
                row_entries.append((var, e))
            self.entries.append(row_entries)

        ctrl = tk.Frame(self, bg=C["panel"])
        ctrl.pack(fill="x", padx=24, pady=(6, 10))
        self._label(ctrl, "Pembagi (Divisor):").grid(row=0, column=0, sticky="w", pady=2)
        self.div_var = tk.StringVar(value="auto")
        _make_entry(ctrl, self.div_var, width=10).grid(row=0, column=1, padx=8, pady=2)
        self._label(ctrl, "(kosong / 'auto' = jumlah bobot kernel)", muted=True).grid(row=0, column=2, sticky="w")

        self._label(ctrl, "Offset Nilai (+):").grid(row=1, column=0, sticky="w", pady=2)
        self.offset_var = tk.StringVar(value="0")
        _make_entry(ctrl, self.offset_var, width=10).grid(row=1, column=1, padx=8, pady=2)
        self.div_var.trace_add("write", lambda *a: self._on_change())
        self.offset_var.trace_add("write", lambda *a: self._on_change())

        preset_box = tk.Frame(self, bg=C["panel"])
        preset_box.pack(fill="x", padx=24, pady=(4, 10))
        self._label(preset_box, "Pilih Preset Kernel:", muted=True).pack(side="left")
        self.preset_choice = tk.StringVar(value=self.PRESETS[0][0])
        opt = ttk.Combobox(preset_box, textvariable=self.preset_choice,
                           values=[p[0] for p in self.PRESETS], state="readonly", width=34)
        opt.pack(side="left", padx=8)
        opt.bind("<<ComboboxSelected>>", self._load_preset)

        self._buttons()
        self.after(80, self._on_change)

    def _load_preset(self, _e=None):
        name = self.preset_choice.get()
        for p_name, mat, div, off in self.PRESETS:
            if p_name == name:
                for r in range(3):
                    for c in range(3):
                        self.entries[r][c][0].set(str(mat[r][c]))
                self.div_var.set("auto" if div is None else str(div))
                self.offset_var.set(str(off))
                break

    def get_data(self) -> Tuple[np.ndarray, Optional[float], float]:
        mat = np.zeros((3, 3), dtype=np.float32)
        for r in range(3):
            for c in range(3):
                mat[r, c] = float(self.entries[r][c][0].get() or 0)
        div_str = self.div_var.get().strip().lower()
        div = None if (not div_str or div_str == "auto") else float(div_str)
        offset = float(self.offset_var.get() or 0)
        return mat, div, offset

    def _on_change(self):
        try:
            mat, div, offset = self.get_data()
            self.preview(mat, div, offset)
        except Exception:
            pass

    def _ok(self):
        try:
            self.result = self.get_data()
            self.destroy()
        except ValueError as exc:
            messagebox.showwarning("Konvolusi", f"Input kernel tidak valid:\n{exc}", parent=self)


class ArithmeticDialog(BaseDialog):
    """Dialog Operasi Aritmatika Citra (Add, Substract, Multiply, Divide)."""

    def __init__(self, parent, op: str, current_img: Image.Image, preview: Callable[[Image.Image], None]):
        titles = {
            "add": "Penjumlahan Citra (Add +)",
            "sub": "Pengurangan Citra (Substract -)",
            "mul": "Perkalian Citra (Multiply *)",
            "div": "Pembagian Citra (Divide /)",
        }
        super().__init__(parent, titles.get(op, "Aritmatika Citra"))
        self.op = op
        self.current_img = current_img
        self.preview = preview
        self.other_img: Optional[Image.Image] = None

        body = tk.Frame(self, bg=C["panel"])
        body.pack(padx=24, pady=(18, 8), fill="x")

        self.mode_var = tk.StringVar(value="scalar")
        rb1 = tk.Radiobutton(body, text="Dengan Nilai Skalar / Slider", value="scalar",
                             variable=self.mode_var, command=self._update_ui,
                             bg=C["panel"], fg=C["text"], selectcolor=C["input"], font=(FONT, 10))
        rb2 = tk.Radiobutton(body, text="Dengan Citra Kedua (Muat File)", value="image",
                             variable=self.mode_var, command=self._update_ui,
                             bg=C["panel"], fg=C["text"], selectcolor=C["input"], font=(FONT, 10))
        rb1.pack(anchor="w", pady=2)
        rb2.pack(anchor="w", pady=2)

        self.scalar_frame = tk.Frame(body, bg=C["panel"])
        self.scalar_frame.pack(fill="x", pady=8)
        default_val = 1.5 if op in ("mul", "div") else 30.0
        min_val = 0.1 if op in ("mul", "div") else 0.0
        max_val = 5.0 if op in ("mul", "div") else 255.0
        self.slider_var = tk.DoubleVar(value=default_val)
        self.lbl_scalar = tk.Label(self.scalar_frame, text=f"Nilai: {default_val}",
                                   bg=C["panel"], fg=C["accent_h"], font=(FONT_MONO, 10, "bold"))
        self.lbl_scalar.pack(anchor="w")
        self.scale = ttk.Scale(self.scalar_frame, from_=min_val, to=max_val,
                               variable=self.slider_var, style="Studio.Horizontal.TScale",
                               command=self._on_slider)
        self.scale.pack(fill="x", pady=4)

        self.img_frame = tk.Frame(body, bg=C["panel"])
        self.btn_load = HoverButton(self.img_frame, "Pilih Gambar Kedua…", self._load_second_img, style="accent", padx=12, pady=4)
        self.btn_load.pack(side="left")
        self.lbl_img_path = tk.Label(self.img_frame, text="Belum ada gambar kedua", bg=C["panel"],
                                     fg=C["muted"], font=(FONT, 9))
        self.lbl_img_path.pack(side="left", padx=10)

        self._buttons()
        self._update_ui()
        self.after(60, self._render_preview)

    def _update_ui(self):
        if self.mode_var.get() == "scalar":
            self.img_frame.pack_forget()
            self.scalar_frame.pack(fill="x", pady=8)
        else:
            self.scalar_frame.pack_forget()
            self.img_frame.pack(fill="x", pady=8)
        self._render_preview()

    def _on_slider(self, _v=None):
        val = self.slider_var.get()
        txt = f"{val:.2f}" if self.op in ("mul", "div") else f"{int(round(val))}"
        self.lbl_scalar.configure(text=f"Nilai: {txt}")
        self._render_preview()

    def _load_second_img(self):
        path = filedialog.askopenfilename(title="Pilih gambar kedua untuk operasi aritmatika",
                                          filetypes=OPEN_TYPES, parent=self)
        if not path:
            return
        try:
            im, _ = ops.load_image(path)
            self.other_img = im
            self.lbl_img_path.configure(text=os.path.basename(path), fg=C["text"])
            self._render_preview()
        except Exception as exc:
            messagebox.showerror("Error", f"Gagal membuka citra:\n{exc}", parent=self)

    def _render_preview(self):
        try:
            if self.mode_var.get() == "scalar":
                res = ops.arithmetic_op(self.current_img, self.op, scalar=self.slider_var.get(), other_img=None)
            else:
                if self.other_img is not None:
                    res = ops.arithmetic_op(self.current_img, self.op, scalar=0, other_img=self.other_img)
                else:
                    return
            self.preview(res)
        except Exception:
            pass

    def _ok(self):
        if self.mode_var.get() == "scalar":
            val = self.slider_var.get()
            self.result = lambda im: ops.arithmetic_op(im, self.op, scalar=val, other_img=None)
        else:
            if self.other_img is None:
                messagebox.showwarning("Aritmatika", "Silakan pilih gambar kedua terlebih dahulu.", parent=self)
                return
            other = self.other_img
            self.result = lambda im: ops.arithmetic_op(im, self.op, scalar=0, other_img=other)
        self.destroy()


class BooleanDialog(BaseDialog):
    """Dialog Operasi Boolean Citra (AND, OR, XOR)."""

    def __init__(self, parent, op: str, current_img: Image.Image, preview: Callable[[Image.Image], None]):
        super().__init__(parent, f"Operasi Boolean ({op.upper()})")
        self.op = op
        self.current_img = current_img
        self.preview = preview
        self.other_img: Optional[Image.Image] = None

        body = tk.Frame(self, bg=C["panel"])
        body.pack(padx=24, pady=(18, 8), fill="x")

        self.mode_var = tk.StringVar(value="mask")
        rb1 = tk.Radiobutton(body, text="Dengan Masker Biner (Nilai 0–255)", value="mask",
                             variable=self.mode_var, command=self._update_ui,
                             bg=C["panel"], fg=C["text"], selectcolor=C["input"], font=(FONT, 10))
        rb2 = tk.Radiobutton(body, text="Dengan Citra Kedua (Muat File)", value="image",
                             variable=self.mode_var, command=self._update_ui,
                             bg=C["panel"], fg=C["text"], selectcolor=C["input"], font=(FONT, 10))
        rb1.pack(anchor="w", pady=2)
        rb2.pack(anchor="w", pady=2)

        self.mask_frame = tk.Frame(body, bg=C["panel"])
        self.mask_frame.pack(fill="x", pady=8)
        self.mask_var = tk.DoubleVar(value=128)
        self.lbl_mask = tk.Label(self.mask_frame, text="Masker: 128 (0x80)",
                                 bg=C["panel"], fg=C["accent_h"], font=(FONT_MONO, 10, "bold"))
        self.lbl_mask.pack(anchor="w")
        self.scale = ttk.Scale(self.mask_frame, from_=0, to=255,
                               variable=self.mask_var, style="Studio.Horizontal.TScale",
                               command=self._on_slider)
        self.scale.pack(fill="x", pady=4)

        self.img_frame = tk.Frame(body, bg=C["panel"])
        self.btn_load = HoverButton(self.img_frame, "Pilih Gambar Kedua…", self._load_second_img, style="accent", padx=12, pady=4)
        self.btn_load.pack(side="left")
        self.lbl_img_path = tk.Label(self.img_frame, text="Belum ada gambar kedua", bg=C["panel"],
                                     fg=C["muted"], font=(FONT, 9))
        self.lbl_img_path.pack(side="left", padx=10)

        self._buttons()
        self._update_ui()
        self.after(60, self._render_preview)

    def _update_ui(self):
        if self.mode_var.get() == "mask":
            self.img_frame.pack_forget()
            self.mask_frame.pack(fill="x", pady=8)
        else:
            self.mask_frame.pack_forget()
            self.img_frame.pack(fill="x", pady=8)
        self._render_preview()

    def _on_slider(self, _v=None):
        val = int(round(self.mask_var.get()))
        self.lbl_mask.configure(text=f"Masker: {val} (0x{val:02X})")
        self._render_preview()

    def _load_second_img(self):
        path = filedialog.askopenfilename(title="Pilih gambar kedua untuk operasi boolean",
                                          filetypes=OPEN_TYPES, parent=self)
        if not path:
            return
        try:
            im, _ = ops.load_image(path)
            self.other_img = im
            self.lbl_img_path.configure(text=os.path.basename(path), fg=C["text"])
            self._render_preview()
        except Exception as exc:
            messagebox.showerror("Error", f"Gagal membuka citra:\n{exc}", parent=self)

    def _render_preview(self):
        try:
            if self.mode_var.get() == "mask":
                res = ops.boolean_op(self.current_img, self.op, mask_val=int(round(self.mask_var.get())))
            else:
                if self.other_img is not None:
                    res = ops.boolean_op(self.current_img, self.op, other_img=self.other_img)
                else:
                    return
            self.preview(res)
        except Exception:
            pass

    def _ok(self):
        if self.mode_var.get() == "mask":
            val = int(round(self.mask_var.get()))
            self.result = lambda im: ops.boolean_op(im, self.op, mask_val=val)
        else:
            if self.other_img is None:
                messagebox.showwarning("Boolean", "Silakan pilih gambar kedua terlebih dahulu.", parent=self)
                return
            other = self.other_img
            self.result = lambda im: ops.boolean_op(im, self.op, other_img=other)
        self.destroy()


class PseudocolorDialog(BaseDialog):
    """Dialog Pemilihan Colormap untuk Citra Semu (Pseudocolor)."""

    COLORMAPS = [
        "jet", "viridis", "plasma", "inferno", "magma",
        "cividis", "hot", "cool", "rainbow", "turbo", "bone"
    ]

    def __init__(self, parent, preview: Callable[[str], None]):
        super().__init__(parent, "Pseudocolor (Pemberian Warna Semu)")
        self.preview = preview

        body = tk.Frame(self, bg=C["panel"])
        body.pack(padx=24, pady=(18, 8))

        self._label(body, "Pilih Skema Warna Semu (Colormap):").pack(anchor="w", pady=(0, 6))
        self.choice = tk.StringVar(value="jet")
        combo = ttk.Combobox(body, textvariable=self.choice, values=self.COLORMAPS, state="readonly", width=26)
        combo.pack(fill="x", pady=4)
        combo.bind("<<ComboboxSelected>>", lambda e: self._update())

        self._buttons()
        self.after(60, self._update)

    def _update(self):
        self.preview(self.choice.get())

    def _ok(self):
        self.result = self.choice.get()
        self.destroy()


class AboutDialog(BaseDialog):
    """
    Dialog Tentang Tim Pengembang Visionary & Tutorial Pembelajaran.
    Didesain mewah, elegan, dan informatif.
    """

    GITHUB_URL = "https://github.com"
    YOUTUBE_URL = "https://youtube.com"

    def __init__(self, parent):
        super().__init__(parent, "About - Info Tim Visionary & Tutorial")

        # Container Utama
        card = tk.Frame(self, bg=C["panel"], padx=26, pady=22)
        card.pack(fill="both", expand=True)

        # Header Badge
        badge_row = tk.Frame(card, bg=C["panel"])
        badge_row.pack(fill="x", pady=(0, 4))
        tk.Label(
            badge_row, text=f"✦ TIM {TEAM_NAME.upper()} ✦",
            bg=C["card"], fg=C["accent_glow"], font=(FONT_DISPLAY, 9, "bold"),
            padx=10, pady=2, highlightthickness=1, highlightbackground=C["border_light"]
        ).pack(side="left")

        # Judul Aplikasi
        tk.Label(
            card, text="Image Processing Studio", bg=C["panel"], fg=C["text"],
            font=(FONT_DISPLAY, 16, "bold")
        ).pack(anchor="w", pady=(6, 2))

        tk.Label(
            card,
            text=f"Aplikasi Pengolahan Citra Digital (PCD) • Update: {UPDATE_DATE}\n{COPYRIGHT_TEXT}",
            bg=C["panel"], fg=C["muted"], font=(FONT, 9), justify="left"
        ).pack(anchor="w", pady=(0, 14))

        # Box Anggota Tim Visionary
        team_frame = tk.LabelFrame(
            card, text="  ✦ Tim Developer: Visionary  ", bg=C["card"], fg=C["accent_h"],
            font=(FONT_DISPLAY, 10, "bold"), bd=1, relief="solid", highlightbackground=C["border"]
        )
        team_frame.pack(fill="x", pady=(0, 12))

        inner_team = tk.Frame(team_frame, bg=C["card"], padx=14, pady=10)
        inner_team.pack(fill="x")

        tk.Label(
            inner_team, text="Mata Kuliah : Pengolahan Citra Digital (PCD)",
            bg=C["card"], fg=C["text_sub"], font=(FONT, 10, "bold")
        ).pack(anchor="w", pady=(0, 8))

        # Daftar Anggota Tim
        for idx, (nama, nim) in enumerate(TEAM_MEMBERS, start=1):
            row_m = tk.Frame(inner_team, bg=C["card"])
            row_m.pack(fill="x", pady=2)
            tk.Label(row_m, text=f"{idx}.", bg=C["card"], fg=C["accent_h"], font=(FONT_MONO, 10, "bold"), width=3).pack(side="left")
            tk.Label(row_m, text=nama, bg=C["card"], fg=C["text"], font=(FONT, 10, "bold")).pack(side="left")
            tk.Label(row_m, text=f"({nim})", bg=C["card"], fg=C["muted"], font=(FONT_MONO, 10)).pack(side="left", padx=8)

        # Box Tutorial Link
        tut_frame = tk.LabelFrame(
            card, text="  ✦ Tutorial Pembelajaran  ", bg=C["card"], fg=C["ok"],
            font=(FONT_DISPLAY, 10, "bold"), bd=1, relief="solid", highlightbackground=C["border"]
        )
        tut_frame.pack(fill="x", pady=(0, 14))

        inner_tut = tk.Frame(tut_frame, bg=C["card"], padx=14, pady=10)
        inner_tut.pack(fill="x")

        gh_row = tk.Frame(inner_tut, bg=C["card"])
        gh_row.pack(fill="x", pady=4)
        tk.Label(gh_row, text="✓ Link Github    :", bg=C["card"], fg=C["text_sub"], font=(FONT, 10)).pack(side="left")
        HoverButton(gh_row, "Buka Repositori Github ↗", lambda: webbrowser.open(self.GITHUB_URL),
                    style="accent", padx=14, pady=4).pack(side="left", padx=10)

        yt_row = tk.Frame(inner_tut, bg=C["card"])
        yt_row.pack(fill="x", pady=4)
        tk.Label(yt_row, text="✓ Link Youtube  :", bg=C["card"], fg=C["text_sub"], font=(FONT, 10)).pack(side="left")
        HoverButton(yt_row, "Buka Video Tutorial Youtube ↗", lambda: webbrowser.open(self.YOUTUBE_URL),
                    style="purple", padx=14, pady=4).pack(side="left", padx=10)

        # Tombol Tutup
        btn_row = tk.Frame(card, bg=C["panel"])
        btn_row.pack(fill="x")
        HoverButton(btn_row, "Tutup", self.destroy, style="accent", padx=24, pady=6).pack(side="right")


# ==========================================================================
# Aplikasi Utama GUI (ImageStudioApp)
# ==========================================================================
class ImageStudioApp:
    MAX_HISTORY = 20

    def __init__(self, root: tk.Tk):
        self.root = root
        self.original: Optional[Image.Image] = None
        self.current: Optional[Image.Image] = None
        self.path: Optional[str] = None
        self.format: Optional[str] = None
        self.history: List[tuple] = []
        self.op_log: List[str] = []
        self.dirty = False
        self._hist_windows: List[hist.HistogramWindow] = []

        self._setup_window()
        self._setup_style()
        self._build_menu()
        self._build_layout()
        self._bind_keys()
        self._refresh_all()

    def _setup_window(self) -> None:
        self.root.title(APP_NAME)
        self.root.configure(bg=C["bg"])
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(1400, int(sw * 0.94)), min(860, int(sh * 0.92))
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 3)}")
        self.root.minsize(1080, 680)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _setup_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Vertical.TScrollbar", background=C["btn_h"], troughcolor=C["sidebar"],
            bordercolor=C["sidebar"], lightcolor=C["btn_h"], darkcolor=C["btn_h"],
            arrowcolor=C["muted"], relief="flat",
        )
        style.configure(
            "Studio.Horizontal.TScale", background=C["accent"], troughcolor=C["input"],
            bordercolor=C["border"], lightcolor=C["accent"], darkcolor=C["accent"],
        )
        style.map("Studio.Horizontal.TScale", background=[("active", C["accent_h"])])

    def _bind_keys(self) -> None:
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_image())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-q>", lambda e: self.exit_app())

    # ======================================================================
    # STRUKTUR MENU BAR (SESUAI DOKUMEN PANDUAN PCD)
    # ======================================================================
    def _build_menu(self) -> None:
        opts = dict(bg=C["panel"], fg=C["text"], activebackground=C["accent"],
                    activeforeground="white", bd=0, relief="flat", tearoff=0, font=(FONT, 10))
        bar = tk.Menu(self.root, **opts)

        # 1. File
        m_file = tk.Menu(bar, **opts)
        m_file.add_command(label="Open…", accelerator="Ctrl+O", command=self.open_image)
        m_file.add_command(label="Save", accelerator="Ctrl+S", command=self.save_image)
        m_file.add_command(label="Save As…", accelerator="Ctrl+Shift+S", command=self.save_as_image)
        m_file.add_separator()
        m_file.add_command(label="Exit", accelerator="Ctrl+Q", command=self.exit_app)
        bar.add_cascade(label="File", menu=m_file)

        # 2. Basic Ops
        m_basic = tk.Menu(bar, **opts)
        m_basic.add_command(label="Negative", command=self.negative)

        m_arith = tk.Menu(m_basic, **opts)
        m_arith.add_command(label="Add (+)", command=lambda: self.arithmetic_dialog("add"))
        m_arith.add_command(label="Substract (-)", command=lambda: self.arithmetic_dialog("sub"))
        m_arith.add_command(label="Multiply (*)", command=lambda: self.arithmetic_dialog("mul"))
        m_arith.add_command(label="Divide (/)", command=lambda: self.arithmetic_dialog("div"))
        m_basic.add_cascade(label="Arithmetic -->", menu=m_arith)

        m_bool = tk.Menu(m_basic, **opts)
        m_bool.add_command(label="NOT", command=self.boolean_not)
        m_bool.add_command(label="AND", command=lambda: self.boolean_dialog("and"))
        m_bool.add_command(label="OR", command=lambda: self.boolean_dialog("or"))
        m_bool.add_command(label="XOR", command=lambda: self.boolean_dialog("xor"))
        m_basic.add_cascade(label="Boolean -->", menu=m_bool)

        m_geom = tk.Menu(m_basic, **opts)
        m_geom.add_command(label="Translation", command=self.translate_dialog)
        m_geom.add_command(label="Rotation", command=self.rotate_dialog)
        m_geom.add_command(label="Zooming", command=self.zoom_dialog)
        m_geom.add_command(label="Flipping", command=self.flip_dialog)
        m_geom.add_command(label="Cropping", command=self.crop_dialog)
        m_basic.add_cascade(label="Geometrics -->", menu=m_geom)

        m_basic.add_command(label="Thresholding", command=self.threshold_dialog)
        m_basic.add_command(label="Convolution", command=self.convolution_dialog)
        m_basic.add_command(label="Fourier Transform", command=self.fourier_transform_view)

        m_color = tk.Menu(m_basic, **opts)
        m_color.add_command(label="Binary", command=self.color_binary)
        m_color.add_command(label="Grayscale", command=self.color_grayscale)
        m_color.add_command(label="RGB", command=self.color_rgb)
        m_color.add_command(label="HSV", command=self.color_hsv)
        m_color.add_command(label="CMY", command=self.color_cmy)
        m_color.add_command(label="YUV", command=self.color_yuv)
        m_color.add_command(label="YIQ", command=self.color_yiq)
        m_color.add_command(label="Pseudo", command=self.color_pseudo)
        m_basic.add_cascade(label="Colouring -->", menu=m_color)

        bar.add_cascade(label="Basic Ops", menu=m_basic)

        # 3. Enhancement
        m_enh = tk.Menu(bar, **opts)
        m_enh.add_command(label="Brightness", command=self.brightness_dialog)
        m_enh.add_command(label="Contrast", command=self.contrast_dialog)
        m_enh.add_command(label="Hist. Equalization", command=self.hist_equalization)

        m_smooth = tk.Menu(m_enh, **opts)
        m_smooth_sp = tk.Menu(m_smooth, **opts)
        m_smooth_sp.add_command(label="Lowpass Filtering", command=self.smooth_lowpass_dialog)
        m_smooth_sp.add_command(label="Median Filtering", command=self.smooth_median_dialog)
        m_smooth.add_cascade(label="Spatial Domain -->", menu=m_smooth_sp)

        m_smooth_fq = tk.Menu(m_smooth, **opts)
        m_smooth_fq.add_command(label="ILPF", command=self.filter_ilpf_dialog)
        m_smooth_fq.add_command(label="BLPF", command=self.filter_blpf_dialog)
        m_smooth.add_cascade(label="Frequency Domain -->", menu=m_smooth_fq)
        m_enh.add_cascade(label="Smoothing -->", menu=m_smooth)

        m_sharp = tk.Menu(m_enh, **opts)
        m_sharp_sp = tk.Menu(m_sharp, **opts)
        m_sharp_sp.add_command(label="Highpass Filtering", command=self.sharp_highpass)
        m_sharp_sp.add_command(label="Highboost Filtering", command=self.sharp_highboost_dialog)
        m_sharp.add_cascade(label="Spatial Domain -->", menu=m_sharp_sp)

        m_sharp_fq = tk.Menu(m_sharp, **opts)
        m_sharp_fq.add_command(label="IHPF", command=self.filter_ihpf_dialog)
        m_sharp_fq.add_command(label="BHPF", command=self.filter_bhpf_dialog)
        m_sharp.add_cascade(label="Frequency Domain -->", menu=m_sharp_fq)
        m_enh.add_cascade(label="Sharpening -->", menu=m_sharp)

        m_enh.add_command(label="Geometrics correction", command=self.geometrics_correction_dialog)
        bar.add_cascade(label="Enhancement", menu=m_enh)

        # 4. Noise
        m_noise = tk.Menu(bar, **opts)
        m_noise.add_command(label="Gaussian Noise", command=self.noise_gaussian_dialog)
        m_noise.add_command(label="Rayleigh Noise", command=self.noise_rayleigh_dialog)
        m_noise.add_command(label="Erlang (Gamma) Noise", command=self.noise_erlang_dialog)
        m_noise.add_command(label="Exponential Noise", command=self.noise_exponential_dialog)
        m_noise.add_command(label="Uniform Noise", command=self.noise_uniform_dialog)
        m_noise.add_command(label="Impulse Noise", command=self.noise_impulse_dialog)
        bar.add_cascade(label="Noise", menu=m_noise)

        # 5. Edge Detection
        m_edge = tk.Menu(bar, **opts)
        m_grad1 = tk.Menu(m_edge, **opts)
        m_grad1.add_command(label="Sobel", command=self.edge_sobel)
        m_grad1.add_command(label="Prewit", command=self.edge_prewitt)
        m_grad1.add_command(label="Robert", command=self.edge_roberts)
        m_edge.add_cascade(label="1’st Differential Gradient -->", menu=m_grad1)

        m_grad2 = tk.Menu(m_edge, **opts)
        m_grad2.add_command(label="Laplacian", command=self.edge_laplacian)
        m_grad2.add_command(label="Laplacian of Gaussian (LoG)", command=self.edge_log_dialog)
        m_grad2.add_command(label="Canny", command=self.edge_canny_dialog)
        m_edge.add_cascade(label="2’nd Differential Gradient -->", menu=m_grad2)

        m_edge.add_command(label="Compass", command=self.edge_compass)
        bar.add_cascade(label="Edge Detection", menu=m_edge)

        # 6. Segmentation
        m_seg = tk.Menu(bar, **opts)
        m_seg.add_command(label="Global Thresholding", command=self.seg_global_thresh_dialog)
        m_seg.add_command(label="Otsu Thresholding", command=self.seg_otsu)
        m_seg.add_command(label="Adaptive Thresholding", command=self.seg_adaptive_dialog)
        m_seg.add_command(label="K-Means Clustering", command=self.seg_kmeans_dialog)
        m_seg.add_command(label="Region Growing", command=self.seg_region_growing_dialog)
        m_seg.add_command(label="Watershed", command=self.seg_watershed)
        bar.add_cascade(label="Segmentation", menu=m_seg)

        # 7. About
        m_about = tk.Menu(bar, **opts)
        m_about.add_command(label="Info Tim developer", command=self.about_dialog)
        m_about.add_separator()
        m_about.add_command(label="Tutorial : Link Github", command=lambda: webbrowser.open(AboutDialog.GITHUB_URL))
        m_about.add_command(label="Tutorial : Link Youtube", command=lambda: webbrowser.open(AboutDialog.YOUTUBE_URL))
        bar.add_cascade(label="About", menu=m_about)

        self.root.configure(menu=bar)
        self.menuBar = bar

    # Aliases untuk kompatibilitas kurikulum / grading script
    def menuOpen_click(self) -> None:
        self.open_image()

    def menuSave_click(self) -> None:
        self.save_image()

    def menuExit_click(self) -> None:
        self.exit_app()

    # ======================================================================
    # TATA LETAK GUI UTAMA (SIDEBAR & WORKSPACE)
    # ======================================================================
    def _build_layout(self) -> None:
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # ---- Sidebar Kiri (Lebar 290px agar font lebih besar dan nyaman dibaca)
        side = tk.Frame(self.root, bg=C["sidebar"], width=290, highlightthickness=1, highlightbackground=C["border"])
        side.grid(row=0, column=0, sticky="ns")
        side.grid_propagate(False)
        side.pack_propagate(False)

        # Brand Banner Visionary
        brand = tk.Frame(side, bg=C["card"], padx=14, pady=12, highlightthickness=1, highlightbackground=C["border"])
        brand.pack(fill="x", padx=10, pady=(12, 8))

        badge_box = tk.Frame(brand, bg=C["card"])
        badge_box.pack(fill="x")
        tk.Label(
            badge_box, text=f"✦ {TEAM_NAME.upper()} ✦",
            bg=C["accent"], fg="white", font=(FONT_DISPLAY, 10, "bold"),
            padx=8, pady=2
        ).pack(side="left")

        tk.Label(
            brand, text="Image Processing Studio", bg=C["card"], fg=C["text"],
            font=(FONT_DISPLAY, 12, "bold")
        ).pack(anchor="w", pady=(6, 1))

        tk.Label(
            brand, text=f"PCD 2026 • {UPDATE_DATE}", bg=C["card"], fg=C["muted"],
            font=(FONT_MONO, 9)
        ).pack(anchor="w")

        # ScrollFrame Sidebar
        scroll = ScrollFrame(side, C["sidebar"], width=275)
        scroll.pack(fill="both", expand=True, pady=(0, 6))
        inner = scroll.inner

        sections = [
            ("FILE", [
                ("Open", self.open_image, "side"),
                ("Save", self.save_image, "side"),
                ("Save As", self.save_as_image, "side"),
                ("Reset Asli", self.reset_image, "side"),
                ("Undo", self.undo, "side"),
                ("Exit", self.exit_app, "danger"),
            ]),
            ("BASIC OPS", [
                ("Negative", self.negative, "side"),
                ("Arithmetic", lambda: self.arithmetic_dialog("add"), "side"),
                ("Boolean (AND/OR/XOR)", lambda: self.boolean_dialog("and"), "side"),
                ("Translation", self.translate_dialog, "side"),
                ("Rotation", self.rotate_dialog, "side"),
                ("Zooming", self.zoom_dialog, "side"),
                ("Flipping", self.flip_dialog, "side"),
                ("Cropping", self.crop_dialog, "side"),
                ("Thresholding", self.threshold_dialog, "side"),
                ("Convolution (3×3)", self.convolution_dialog, "side"),
                ("Fourier Transform", self.fourier_transform_view, "side"),
                ("Colouring (HSV/CMY/YUV)", self.color_hsv, "side"),
            ]),
            ("ENHANCEMENT", [
                ("Brightness", self.brightness_dialog, "side"),
                ("Contrast", self.contrast_dialog, "side"),
                ("Hist. Equalization", self.hist_equalization, "side"),
                ("Lowpass (Spatial)", self.smooth_lowpass_dialog, "side"),
                ("Median Filter", self.smooth_median_dialog, "side"),
                ("ILPF / BLPF (Freq)", self.filter_ilpf_dialog, "side"),
                ("Highpass / Highboost", self.sharp_highboost_dialog, "side"),
                ("Geometrics Correction", self.geometrics_correction_dialog, "side"),
            ]),
            ("NOISE", [
                ("Gaussian Noise", self.noise_gaussian_dialog, "side"),
                ("Rayleigh Noise", self.noise_rayleigh_dialog, "side"),
                ("Erlang (Gamma) Noise", self.noise_erlang_dialog, "side"),
                ("Exponential Noise", self.noise_exponential_dialog, "side"),
                ("Uniform Noise", self.noise_uniform_dialog, "side"),
                ("Impulse (Salt & Pepper)", self.noise_impulse_dialog, "side"),
            ]),
            ("EDGE DETECTION", [
                ("Sobel", self.edge_sobel, "side"),
                ("Prewitt", self.edge_prewitt, "side"),
                ("Roberts Cross", self.edge_roberts, "side"),
                ("Laplacian", self.edge_laplacian, "side"),
                ("LoG (Laplacian of Gauss)", self.edge_log_dialog, "side"),
                ("Canny Edge", self.edge_canny_dialog, "side"),
                ("Compass (Kirsch)", self.edge_compass, "side"),
            ]),
            ("SEGMENTATION", [
                ("Otsu Threshold", self.seg_otsu, "side"),
                ("Adaptive Threshold", self.seg_adaptive_dialog, "side"),
                ("K-Means Clustering", self.seg_kmeans_dialog, "side"),
                ("Region Growing", self.seg_region_growing_dialog, "side"),
                ("Watershed", self.seg_watershed, "side"),
            ]),
            ("HISTOGRAM", [
                ("Histogram RGB", self.show_rgb_histogram, "side"),
                ("Histogram Grayscale", self.show_gray_histogram, "side"),
            ]),
        ]

        for title, buttons in sections:
            sec_header = tk.Frame(inner, bg=C["sidebar"])
            sec_header.pack(fill="x", padx=14, pady=(12, 3))
            tk.Label(sec_header, text=f"• {title}", bg=C["sidebar"], fg=C["accent_glow"], font=(FONT_DISPLAY, 9, "bold"),
                     anchor="w").pack(side="left")
            for text, cmd, style in buttons:
                HoverButton(inner, "  " + text, cmd, style=style, anchor="w", pady=5).pack(
                    fill="x", padx=10, pady=1)
        tk.Frame(inner, bg=C["sidebar"], height=18).pack()

        # ---- Area Konten Tengah
        content = tk.Frame(self.root, bg=C["bg"])
        content.grid(row=0, column=1, sticky="nsew", padx=(14, 14), pady=(12, 0))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Header Bar
        header = tk.Frame(content, bg=C["bg"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        title_box = tk.Frame(header, bg=C["bg"])
        title_box.pack(side="left")
        self.title_var = tk.StringVar(value="Belum ada gambar yang dimuat")
        tk.Label(title_box, textvariable=self.title_var, bg=C["bg"], fg=C["text"],
                 font=(FONT_DISPLAY, 15, "bold")).pack(side="left")

        self.badge_var = tk.StringVar(value="")
        self.badge = tk.Label(header, textvariable=self.badge_var, bg=C["bg"], fg=C["ok"], font=(FONT, 10, "bold"))
        self.badge.pack(side="right")
        HoverButton(header, "Buka Gambar", self.open_image, style="accent", padx=18, pady=5).pack(side="right", padx=10)

        # Area Pratinjau Citra (Dual Canvas)
        previews = tk.Frame(content, bg=C["bg"])
        previews.grid(row=1, column=0, sticky="nsew")
        previews.grid_columnconfigure((0, 1), weight=1, uniform="p")
        previews.grid_rowconfigure(0, weight=1)

        self.panel_orig = ImagePanel(
            previews, "Gambar Asli",
            "Belum ada gambar\n\nBuka file gambar via File → Open atau tekan Ctrl+O",
            dot_color="#38bdf8"
        )
        self.panel_orig.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        self.panel_res = ImagePanel(
            previews, "Hasil Pengolahan Citra",
            "Hasil operasi pengolahan citra akan tampil di sini",
            dot_color="#34d399"
        )
        self.panel_res.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        # Kartu Informasi Metadata
        info = tk.Frame(content, bg=C["bg"])
        info.grid(row=2, column=0, sticky="ew", pady=(12, 12))
        info.grid_columnconfigure((0, 1), weight=1, uniform="i")

        self.card_orig = InfoCard(info, "INFORMASI GAMBAR ASLI", [
            ("name", "Nama file"), ("res", "Resolusi"), ("fmt", "Format"),
            ("size", "Ukuran file"), ("mode", "Mode warna")],
            accent_color="#60a5fa")
        self.card_orig.grid(row=0, column=0, sticky="nsew", padx=(0, 7))

        self.card_res = InfoCard(info, "INFORMASI HASIL PENGOLAHAN", [
            ("res", "Resolusi"), ("fmt", "Format simpan"), ("size", "Ukuran file"),
            ("ops", "Riwayat operasi")],
            accent_color="#34d399")
        self.card_res.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        # ---- Status Bar Bawah
        status = tk.Frame(self.root, bg=C["sidebar"], highlightthickness=1, highlightbackground=C["border"])
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

        status_left = tk.Frame(status, bg=C["sidebar"])
        status_left.pack(side="left", padx=14, pady=5)
        tk.Label(status_left, text="●", bg=C["sidebar"], fg=C["ok"], font=(FONT, 9)).pack(side="left")
        self.status_var = tk.StringVar(value=" Siap. Silakan buka gambar untuk memulai pengolahan citra.")
        tk.Label(status_left, textvariable=self.status_var, bg=C["sidebar"], fg=C["text_sub"],
                 font=(FONT, 10)).pack(side="left")

        tk.Label(
            status, text=f"Tim {TEAM_NAME} • PCD 2026 • Non-destructive editing",
            bg=C["sidebar"], fg=C["muted"], font=(FONT_MONO, 9)
        ).pack(side="right", padx=14)

    # ======================================================================
    # HELPER OPERASI & HISTORI
    # ======================================================================
    def _set_status(self, msg: str) -> None:
        self.status_var.set(f" {msg}")

    def _require(self) -> bool:
        if self.current is None:
            messagebox.showinfo(APP_NAME, "Buka gambar terlebih dahulu (File → Open).", parent=self.root)
            return False
        return True

    def _refresh_all(self) -> None:
        self.panel_orig.set_image(self.original)
        self.panel_res.set_image(self.current)
        self._refresh_info()

    def _refresh_info(self) -> None:
        if self.original is None:
            self.title_var.set("Belum ada gambar yang dimuat")
            self.badge_var.set("")
            self.card_orig.update_info({})
            self.card_res.update_info({})
            return
        name = os.path.basename(self.path or "Citra")
        self.title_var.set(name)
        o = ops.get_image_info(self.original, self.path, self.format)
        self.card_orig.update_info({
            "name": name, "res": f"{o['resolution']}  ({o['megapixels']} MP)",
            "fmt": str(o["format"]), "size": str(o["file_size_text"]), "mode": "RGB (24-bit)",
        })
        r = ops.get_image_info(self.current, None, self.format)
        log = " → ".join(self.op_log) if self.op_log else "Belum ada (sama dengan asli)"
        self.card_res.update_info({
            "res": f"{r['resolution']}  ({r['megapixels']} MP)",
            "fmt": str(r["format"]), "size": str(r["file_size_text"]), "ops": log,
        })
        self.badge_var.set("● Ada perubahan belum disimpan" if self.dirty else "")
        self.badge.configure(fg=C["warn"] if self.dirty else C["ok"])

    def _preview(self, img: Image.Image) -> None:
        self.panel_res.set_image(img)

    def _apply(self, func: Callable[[Image.Image], Image.Image], label: str) -> bool:
        if not self._require():
            return False
        self.root.configure(cursor="watch")
        self.root.update_idletasks()
        try:
            new_img = func(self.current)
        except ValueError as exc:
            messagebox.showwarning(label, str(exc), parent=self.root)
            self.panel_res.set_image(self.current)
            return False
        except Exception as exc:
            messagebox.showerror(label, f"Operasi gagal:\n{exc}", parent=self.root)
            self.panel_res.set_image(self.current)
            return False
        finally:
            self.root.configure(cursor="")

        self.history.append((self.current, list(self.op_log)))
        del self.history[:-self.MAX_HISTORY]
        self.current = new_img
        self.op_log.append(label)
        self.dirty = True
        self._refresh_all()
        self._set_status(f"Berhasil: {label} ({new_img.width} × {new_img.height} px)")
        return True

    def _slider_op(self, title: str, func: Callable[..., Image.Image], fields: List[dict],
                   label_fn: Callable[[dict], str], presets=None, hint: str = "") -> None:
        if not self._require():
            return
        base = self.current

        def preview(values: dict) -> None:
            try:
                self._preview(func(base, **values))
            except Exception:
                pass

        values = SliderDialog(self.root, title, fields, preview, presets, hint).show()
        if values is None:
            self.panel_res.set_image(self.current)
            self._set_status(f"{title} dibatalkan.")
            return
        self._apply(lambda im: func(im, **values), label_fn(values))

    # ======================================================================
    # 1. FILE OPERATIONS
    # ======================================================================
    def open_image(self) -> None:
        if self.dirty and not messagebox.askyesno(
                APP_NAME, "Ada perubahan yang belum disimpan.\nTetap buka gambar lain?", parent=self.root):
            return
        path = filedialog.askopenfilename(title="Buka gambar", filetypes=OPEN_TYPES, parent=self.root)
        if not path:
            return
        try:
            img, fmt = ops.load_image(path)
        except Exception as exc:
            messagebox.showerror("Open", f"Tidak dapat membuka file:\n{exc}", parent=self.root)
            return
        self.original = img
        self.current = img.copy()
        self.path, self.format = path, fmt
        self.history.clear()
        self.op_log.clear()
        self.dirty = False
        self._refresh_all()
        self._set_status(f"Dibuka: {os.path.basename(path)} ({img.width} × {img.height} px)")

    def save_image(self) -> None:
        if not self._require():
            return
        if self.path and os.path.isfile(self.path):
            try:
                size = ops.save_image(self.current, self.path)
                self.dirty = False
                self._refresh_info()
                self._set_status(f"Tersimpan: {self.path} ({ops.format_bytes(size)})")
                messagebox.showinfo("Save", f"File berhasil disimpan ke:\n{self.path}\n\nUkuran: {ops.format_bytes(size)}", parent=self.root)
                return
            except Exception as exc:
                messagebox.showerror("Save", f"Gagal menyimpan:\n{exc}", parent=self.root)
                return
        self.save_as_image()

    def save_as_image(self) -> None:
        if not self._require():
            return
        fmt = ops.normalize_format(self.format)
        ext = FORMAT_EXT.get(fmt, ".png")
        base = os.path.splitext(os.path.basename(self.path or "hasil_pcd"))[0] + "_hasil"
        path = filedialog.asksaveasfilename(
            title="Simpan Hasil Pengolahan Citra", parent=self.root, defaultextension=ext,
            initialfile=base + ext, initialdir=os.path.dirname(self.path or "") or None,
            filetypes=SAVE_TYPES,
        )
        if not path:
            return
        if os.path.splitext(path)[1].lower() not in SAVE_EXTS:
            path += ".png"
        try:
            size = ops.save_image(self.current, path)
        except Exception as exc:
            messagebox.showerror("Save As", f"Gagal menyimpan:\n{exc}", parent=self.root)
            return
        self.path = path
        self.dirty = False
        self._refresh_info()
        self._set_status(f"Tersimpan: {path} ({ops.format_bytes(size)})")
        messagebox.showinfo("Save As", f"File berhasil disimpan ke:\n{path}\n\nUkuran file: {ops.format_bytes(size)}", parent=self.root)

    def reset_image(self) -> None:
        if not self._require():
            return
        if not self.op_log:
            self._set_status("Gambar sudah sama dengan aslinya.")
            return
        self.history.append((self.current, list(self.op_log)))
        del self.history[:-self.MAX_HISTORY]
        self.current = self.original.copy()
        self.op_log.clear()
        self.dirty = False
        self._refresh_all()
        self._set_status("Reset: Hasil dikembalikan ke gambar asli (bisa di-Undo).")

    def undo(self) -> None:
        if not self.history:
            self._set_status("Tidak ada riwayat operasi yang bisa di-Undo.")
            return
        self.current, self.op_log = self.history.pop()
        self.dirty = bool(self.op_log)
        self._refresh_all()
        self._set_status("Undo berhasil.")

    def exit_app(self) -> None:
        if self.dirty and not messagebox.askyesno(
                APP_NAME, "Ada perubahan yang belum disimpan.\nTetap keluar dari aplikasi?", parent=self.root):
            return
        self.root.destroy()

    # ======================================================================
    # 2. BASIC OPS
    # ======================================================================
    def negative(self) -> None:
        self._apply(ops.negative, "Negative")

    def arithmetic_dialog(self, op: str) -> None:
        if not self._require():
            return
        base = self.current
        dlg = ArithmeticDialog(self.root, op, base, self._preview)
        action = dlg.show()
        if action is None:
            self.panel_res.set_image(self.current)
            self._set_status(f"Operasi {op} dibatalkan.")
            return
        labels = {"add": "Add (+)", "sub": "Substract (-)", "mul": "Multiply (*)", "div": "Divide (/)"}
        self._apply(action, f"Aritmatika {labels.get(op, op)}")

    def boolean_not(self) -> None:
        self._apply(lambda im: ops.boolean_op(im, "not"), "Boolean NOT")

    def boolean_dialog(self, op: str) -> None:
        if not self._require():
            return
        base = self.current
        dlg = BooleanDialog(self.root, op, base, self._preview)
        action = dlg.show()
        if action is None:
            self.panel_res.set_image(self.current)
            self._set_status(f"Operasi boolean {op.upper()} dibatalkan.")
            return
        self._apply(action, f"Boolean {op.upper()}")

    def translate_dialog(self) -> None:
        if not self._require():
            return
        w, h = self.current.size
        self._slider_op(
            "Geometrics: Translation",
            lambda im, dx, dy: ops.translate_image(im, dx, dy),
            [
                dict(key="dx", label="Geser Horisontal X (px)", min=-w, max=w, default=0, step=1),
                dict(key="dy", label="Geser Vertikal Y (px)", min=-h, max=h, default=0, step=1),
            ],
            lambda v: f"Translation ({v['dx']:+d}, {v['dy']:+d})",
            presets=[("Tengah", {"dx": 0, "dy": 0}), ("Kanan +50", {"dx": 50, "dy": 0}), ("Bawah +50", {"dx": 0, "dy": 50})],
        )

    def rotate_dialog(self) -> None:
        self._slider_op(
            "Geometrics: Rotation", ops.rotate_image,
            [dict(key="angle", label="Sudut (derajat)", min=-180, max=180, default=0, step=1)],
            lambda v: f"Rotate {v['angle']}°",
            presets=[("90°", {"angle": 90}), ("-90°", {"angle": -90}), ("180°", {"angle": 180})],
        )

    def zoom_dialog(self) -> None:
        self._slider_op(
            "Geometrics: Zooming",
            lambda im, pct: ops.zoom_image(im, pct / 100.0),
            [dict(key="pct", label="Skala Zoom (%)", min=10, max=400, default=100, step=5)],
            lambda v: f"Zoom {v['pct']}%",
            presets=[("50%", {"pct": 50}), ("100%", {"pct": 100}), ("150%", {"pct": 150}), ("200%", {"pct": 200})],
        )

    def flip_dialog(self) -> None:
        if not self._require():
            return
        d = tk.Toplevel(self.root)
        d.title("Geometrics: Flipping")
        d.configure(bg=C["panel"])
        d.transient(self.root)
        d.resizable(False, False)
        tk.Label(d, text="Pilih arah pembalikan citra (Flip):", bg=C["panel"], fg=C["text"],
                 font=(FONT, 10)).pack(padx=22, pady=(18, 10))
        btn_box = tk.Frame(d, bg=C["panel"])
        btn_box.pack(padx=22, pady=(0, 18))

        def _do(mode):
            d.destroy()
            self._apply(lambda im: ops.flip_image(im, mode), f"Flip {mode.capitalize()}")

        HoverButton(btn_box, "Flip Horisontal (Cermin Kiri-Kanan)", lambda: _do("horizontal"), style="accent", padx=12, pady=5).pack(fill="x", pady=3)
        HoverButton(btn_box, "Flip Vertikal (Atas-Bawah)", lambda: _do("vertical"), style="side", padx=12, pady=5).pack(fill="x", pady=3)

    def crop_dialog(self) -> None:
        if not self._require():
            return
        w, h = self.current.size
        dlg = tk.Toplevel(self.root)
        dlg.title("Geometrics: Cropping")
        dlg.configure(bg=C["panel"])
        dlg.transient(self.root)
        dlg.resizable(False, False)

        vars_crop = [tk.StringVar(value="0"), tk.StringVar(value="0"), tk.StringVar(value=str(w)), tk.StringVar(value=str(h))]
        body = tk.Frame(dlg, bg=C["panel"])
        body.pack(padx=22, pady=(18, 8))
        tk.Label(body, text=f"Ukuran Citra: {w} × {h} px", bg=C["panel"], fg=C["muted"], font=(FONT, 10)).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))
        labels = ["Kiri (X1)", "Atas (Y1)", "Kanan (X2)", "Bawah (Y2)"]
        for i, (lab, v) in enumerate(zip(labels, vars_crop)):
            r, col = 1 + i // 2, (i % 2) * 2
            tk.Label(body, text=lab, bg=C["panel"], fg=C["text"], font=(FONT, 9)).grid(row=r, column=col, sticky="w", padx=(0 if col == 0 else 14, 6), pady=4)
            _make_entry(body, v, width=8).grid(row=r, column=col + 1, pady=4)

        row = tk.Frame(dlg, bg=C["panel"])
        row.pack(fill="x", padx=22, pady=(8, 18))

        def _ok():
            try:
                coords = [int(v.get()) for v in vars_crop]
                box = ops.validate_crop_box(coords, (w, h))
                dlg.destroy()
                self._apply(lambda im: ops.crop_image(im, *box), f"Crop {box[2]-box[0]}×{box[3]-box[1]}")
            except Exception as e:
                messagebox.showwarning("Crop", str(e), parent=dlg)

        HoverButton(row, "Terapkan Crop", _ok, style="accent", padx=16, pady=5).pack(side="right")
        HoverButton(row, "Batal", dlg.destroy, style="ghost", padx=14, pady=5).pack(side="right", padx=6)

    def threshold_dialog(self) -> None:
        self._slider_op(
            "Thresholding", ops.threshold,
            [dict(key="value", label="Nilai Ambang Batas (0–255)", min=0, max=255, default=128, step=1)],
            lambda v: f"Threshold {v['value']}",
            presets=[("Gelap (64)", {"value": 64}), ("Tengah (128)", {"value": 128}), ("Terang (192)", {"value": 192})],
        )

    def convolution_dialog(self) -> None:
        if not self._require():
            return
        base = self.current

        def preview(mat, div, offset):
            try:
                self._preview(ops.convolve_matrix(base, mat, div, offset))
            except Exception:
                pass

        dlg = ConvolutionDialog(self.root, preview)
        res = dlg.show()
        if res is None:
            self.panel_res.set_image(self.current)
            self._set_status("Konvolusi dibatalkan.")
            return
        mat, div, offset = res
        self._apply(lambda im: ops.convolve_matrix(im, mat, div, offset), "Convolution 3×3")

    def fourier_transform_view(self) -> None:
        self._apply(ops.fourier_transform, "Fourier Transform (FFT Spectrum)")

    def color_binary(self) -> None:
        self._apply(ops.to_binary, "Colouring: Binary")

    def color_grayscale(self) -> None:
        self._apply(ops.to_grayscale, "Colouring: Grayscale")

    def color_rgb(self) -> None:
        self._slider_op(
            "Colouring: RGB Adjust", ops.adjust_rgb,
            [dict(key="r", label="Red (Merah)", min=-100, max=100, default=0, step=1),
             dict(key="g", label="Green (Hijau)", min=-100, max=100, default=0, step=1),
             dict(key="b", label="Blue (Biru)", min=-100, max=100, default=0, step=1)],
            lambda v: f"RGB (R{v['r']:+d} G{v['g']:+d} B{v['b']:+d})",
            presets=[("Hanya Merah", {"r": 0, "g": -100, "b": -100}),
                     ("Hanya Hijau", {"r": -100, "g": 0, "b": -100}),
                     ("Hanya Biru", {"r": -100, "g": -100, "b": 0})],
        )

    def color_hsv(self) -> None:
        self._apply(ops.to_hsv, "Colouring: HSV")

    def color_cmy(self) -> None:
        self._apply(ops.to_cmy, "Colouring: CMY")

    def color_yuv(self) -> None:
        self._apply(ops.to_yuv, "Colouring: YUV")

    def color_yiq(self) -> None:
        self._apply(ops.to_yiq, "Colouring: YIQ")

    def color_pseudo(self) -> None:
        if not self._require():
            return
        base = self.current
        dlg = PseudocolorDialog(self.root, lambda cmap: self._preview(ops.to_pseudocolor(base, cmap)))
        res = dlg.show()
        if res is None:
            self.panel_res.set_image(self.current)
            self._set_status("Pseudocolor dibatalkan.")
            return
        self._apply(lambda im: ops.to_pseudocolor(im, res), f"Pseudocolor ({res.upper()})")

    # ======================================================================
    # 3. ENHANCEMENT
    # ======================================================================
    def brightness_dialog(self) -> None:
        self._slider_op(
            "Brightness", ops.adjust_brightness,
            [dict(key="value", label="Kecerahan (-100 s.d +100)", min=-100, max=100, default=0, step=1)],
            lambda v: f"Brightness {v['value']:+d}",
        )

    def contrast_dialog(self) -> None:
        self._slider_op(
            "Contrast", ops.adjust_contrast,
            [dict(key="value", label="Kontras (-100 s.d +100)", min=-100, max=100, default=0, step=1)],
            lambda v: f"Contrast {v['value']:+d}",
        )

    def hist_equalization(self) -> None:
        self._apply(ops.histogram_equalization, "Hist. Equalization")

    def smooth_lowpass_dialog(self) -> None:
        self._slider_op(
            "Smoothing: Spatial Lowpass Filtering",
            lambda im, radius: ops.spatial_lowpass(im, radius),
            [dict(key="radius", label="Radius Gaussian Lowpass", min=0.5, max=25.0, default=2.0, step=0.5)],
            lambda v: f"Lowpass r={v['radius']:g}",
        )

    def smooth_median_dialog(self) -> None:
        self._slider_op(
            "Smoothing: Spatial Median Filtering",
            lambda im, size: ops.spatial_median(im, int(size)),
            [dict(key="size", label="Ukuran Jendela Median (Ganjil)", min=3, max=15, default=3, step=2)],
            lambda v: f"Median Filter {int(v['size'])}×{int(v['size'])}",
        )

    def filter_ilpf_dialog(self) -> None:
        self._slider_op(
            "Smoothing: Frequency Domain ILPF",
            lambda im, d0: ops.freq_ilpf(im, d0),
            [dict(key="d0", label="Frekuensi Cutoff (D0)", min=5, max=250, default=50, step=5)],
            lambda v: f"ILPF D0={v['d0']}",
        )

    def filter_blpf_dialog(self) -> None:
        self._slider_op(
            "Smoothing: Frequency Domain BLPF",
            lambda im, d0, n: ops.freq_blpf(im, d0, int(n)),
            [dict(key="d0", label="Frekuensi Cutoff (D0)", min=5, max=250, default=50, step=5),
             dict(key="n", label="Ordo Filter (n)", min=1, max=8, default=2, step=1)],
            lambda v: f"BLPF D0={v['d0']} n={int(v['n'])}",
        )

    def sharp_highpass(self) -> None:
        self._apply(ops.spatial_highpass, "Sharpening: Spatial Highpass")

    def sharp_highboost_dialog(self) -> None:
        self._slider_op(
            "Sharpening: Spatial Highboost Filtering",
            lambda im, a: ops.spatial_highboost(im, a),
            [dict(key="a", label="Faktor Penguat Boost (A ≥ 1.0)", min=1.0, max=4.0, default=1.5, step=0.1)],
            lambda v: f"Highboost A={v['a']:.1f}",
        )

    def filter_ihpf_dialog(self) -> None:
        self._slider_op(
            "Sharpening: Frequency Domain IHPF",
            lambda im, d0: ops.freq_ihpf(im, d0),
            [dict(key="d0", label="Frekuensi Cutoff (D0)", min=5, max=250, default=50, step=5)],
            lambda v: f"IHPF D0={v['d0']}",
        )

    def filter_bhpf_dialog(self) -> None:
        self._slider_op(
            "Sharpening: Frequency Domain BHPF",
            lambda im, d0, n: ops.freq_bhpf(im, d0, int(n)),
            [dict(key="d0", label="Frekuensi Cutoff (D0)", min=5, max=250, default=50, step=5),
             dict(key="n", label="Ordo Filter (n)", min=1, max=8, default=2, step=1)],
            lambda v: f"BHPF D0={v['d0']} n={int(v['n'])}",
        )

    def geometrics_correction_dialog(self) -> None:
        self._slider_op(
            "Geometrics Correction",
            lambda im, sx, sy, bar: ops.geometrics_correction(im, sx, sy, bar),
            [dict(key="sx", label="Koreksi Kemiringan X (Shear X)", min=-50, max=50, default=0, step=1),
             dict(key="sy", label="Koreksi Kemiringan Y (Shear Y)", min=-50, max=50, default=0, step=1),
             dict(key="bar", label="Distorsi Lensa Radial (Barrel / Pincushion)", min=-50, max=50, default=0, step=1)],
            lambda v: f"Geometrics Correction (SX:{v['sx']} SY:{v['sy']} Dist:{v['bar']})",
        )

    # ======================================================================
    # 4. NOISE
    # ======================================================================
    def noise_gaussian_dialog(self) -> None:
        self._slider_op(
            "Gaussian Noise",
            lambda im, std: ops.add_gaussian_noise(im, mean=0, std=std),
            [dict(key="std", label="Deviasi Standar (σ)", min=1, max=100, default=25, step=1)],
            lambda v: f"Gaussian Noise σ={v['std']}",
        )

    def noise_rayleigh_dialog(self) -> None:
        self._slider_op(
            "Rayleigh Noise",
            lambda im, scale: ops.add_rayleigh_noise(im, scale),
            [dict(key="scale", label="Parameter Skala (b)", min=1, max=80, default=20, step=1)],
            lambda v: f"Rayleigh Noise b={v['scale']}",
        )

    def noise_erlang_dialog(self) -> None:
        self._slider_op(
            "Erlang (Gamma) Noise",
            lambda im, a, b: ops.add_erlang_noise(im, int(a), b),
            [dict(key="a", label="Parameter Bentuk (Shape a)", min=1, max=8, default=2, step=1),
             dict(key="b", label="Parameter Skala (Scale b)", min=1, max=40, default=15, step=1)],
            lambda v: f"Erlang Noise (a={int(v['a'])}, b={v['b']})",
        )

    def noise_exponential_dialog(self) -> None:
        self._slider_op(
            "Exponential Noise",
            lambda im, scale: ops.add_exponential_noise(im, scale),
            [dict(key="scale", label="Parameter Skala (1/a)", min=1, max=80, default=20, step=1)],
            lambda v: f"Exponential Noise a={v['scale']}",
        )

    def noise_uniform_dialog(self) -> None:
        self._slider_op(
            "Uniform Noise",
            lambda im, bound: ops.add_uniform_noise(im, -bound, bound),
            [dict(key="bound", label="Rentang Nilai [-a, +a]", min=5, max=100, default=30, step=1)],
            lambda v: f"Uniform Noise ±{v['bound']}",
        )

    def noise_impulse_dialog(self) -> None:
        self._slider_op(
            "Impulse Noise (Salt & Pepper)",
            lambda im, amount: ops.add_impulse_noise(im, amount / 100.0),
            [dict(key="amount", label="Kepadatan Noise (%)", min=1, max=50, default=5, step=1)],
            lambda v: f"Impulse Noise {v['amount']}%",
        )

    # ======================================================================
    # 5. EDGE DETECTION
    # ======================================================================
    def edge_sobel(self) -> None:
        self._apply(ops.sobel_edge, "Edge: Sobel")

    def edge_prewitt(self) -> None:
        self._apply(ops.prewitt_edge, "Edge: Prewit")

    def edge_roberts(self) -> None:
        self._apply(ops.roberts_edge, "Edge: Robert")

    def edge_laplacian(self) -> None:
        self._apply(ops.laplacian_edge, "Edge: Laplacian")

    def edge_log_dialog(self) -> None:
        self._slider_op(
            "Edge: Laplacian of Gaussian (LoG)",
            lambda im, sigma: ops.log_edge(im, sigma),
            [dict(key="sigma", label="Parameter Gaussian Sigma (σ)", min=0.5, max=5.0, default=1.4, step=0.1)],
            lambda v: f"LoG σ={v['sigma']:.1f}",
        )

    def edge_canny_dialog(self) -> None:
        self._slider_op(
            "Edge: Canny Edge Detection",
            lambda im, low, high: ops.canny_edge(im, low, high),
            [dict(key="low", label="Ambang Batas Rendah (Low)", min=0, max=255, default=50, step=1),
             dict(key="high", label="Ambang Batas Tinggi (High)", min=0, max=255, default=150, step=1)],
            lambda v: f"Canny ({v['low']}, {v['high']})",
        )

    def edge_compass(self) -> None:
        self._apply(ops.compass_edge, "Edge: Compass (Kirsch 8 Arah)")

    # ======================================================================
    # 6. SEGMENTATION
    # ======================================================================
    def seg_global_thresh_dialog(self) -> None:
        self._slider_op(
            "Segmentation: Global Thresholding", ops.segment_global_threshold,
            [dict(key="value", label="Nilai Ambang Batas (T)", min=0, max=255, default=128, step=1)],
            lambda v: f"Seg. Global Thresh {v['value']}",
        )

    def seg_otsu(self) -> None:
        self._apply(ops.segment_otsu, "Segmentation: Otsu Thresholding")

    def seg_adaptive_dialog(self) -> None:
        self._slider_op(
            "Segmentation: Adaptive Thresholding",
            lambda im, bs, c: ops.segment_adaptive(im, int(bs), c),
            [dict(key="bs", label="Ukuran Blok Lokal (Block Size)", min=3, max=51, default=15, step=2),
             dict(key="c", label="Konstanta Pengurang C", min=-20, max=20, default=2, step=1)],
            lambda v: f"Seg. Adaptive (BS={int(v['bs'])}, C={v['c']})",
        )

    def seg_kmeans_dialog(self) -> None:
        self._slider_op(
            "Segmentation: K-Means Clustering",
            lambda im, k: ops.segment_kmeans(im, int(k)),
            [dict(key="k", label="Jumlah Klaster (K)", min=2, max=8, default=3, step=1)],
            lambda v: f"Seg. K-Means (K={int(v['k'])})",
        )

    def seg_region_growing_dialog(self) -> None:
        self._slider_op(
            "Segmentation: Region Growing",
            lambda im, thresh: ops.segment_region_growing(im, thresh),
            [dict(key="thresh", label="Toleransi Nilai Intensitas Benih", min=1, max=100, default=20, step=1)],
            lambda v: f"Seg. Region Growing (T={v['thresh']})",
        )

    def seg_watershed(self) -> None:
        self._apply(ops.segment_watershed, "Segmentation: Watershed")

    # ======================================================================
    # 7. HISTOGRAM & ABOUT
    # ======================================================================
    def _show_histogram(self, mode: str) -> None:
        if not self._require():
            return
        self._hist_windows = [w for w in self._hist_windows if w.win.winfo_exists()]
        win = hist.HistogramWindow(
            self.root, lambda: {"Hasil": self.current, "Asli": self.original}, mode)
        self._hist_windows.append(win)
        win.focus()
        self._set_status(f"Histogram {mode.upper()} dibuka.")

    def show_rgb_histogram(self) -> None:
        self._show_histogram("rgb")

    def show_gray_histogram(self) -> None:
        self._show_histogram("gray")

    def about_dialog(self) -> None:
        AboutDialog(self.root).show()


# Alias kelas untuk kompatibilitas kurikulum PCD (GUI_app.ipynb)
ImageProcessingApp = ImageStudioApp


def main() -> None:
    _enable_dpi_awareness()
    root = tk.Tk()
    ImageStudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
