"""
histogram.py
============
Perhitungan dan tampilan histogram (RGB & Grayscale) memakai NumPy + Matplotlib.

* ``compute_*``  : menghitung histogram 256 bin dengan NumPy.
* ``build_*``    : membuat objek ``matplotlib.figure.Figure`` bertema dark navy
                   (tidak memakai pyplot, jadi tidak ada jendela liar).
* ``HistogramWindow`` : jendela Tkinter yang menanam figure Matplotlib dan
                   memungkinkan berpindah antara gambar Asli / Hasil.
"""
from __future__ import annotations

from typing import Callable, Dict

import numpy as np
from matplotlib.figure import Figure
from PIL import Image

# Palet warna modern (selaras dengan tema obsidian navy aplikasi)
BG = "#0b0f19"
PANEL = "#141e34"
GRID = "#223154"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
CH_COLORS = {"R": "#f43f5e", "G": "#10b981", "B": "#3b82f6"}
GRAY_COLOR = "#cbd5e1"


# ==========================================================================
# Perhitungan
# ==========================================================================
def compute_rgb_histogram(img: Image.Image) -> Dict[str, np.ndarray]:
    """Histogram 256 bin untuk kanal R, G, B -> {'R': array, 'G': array, 'B': array}."""
    arr = np.asarray(img.convert("RGB"))
    return {
        name: np.bincount(arr[..., i].ravel(), minlength=256)
        for i, name in enumerate("RGB")
    }


def compute_gray_histogram(img: Image.Image) -> np.ndarray:
    """Histogram 256 bin dari versi grayscale gambar."""
    arr = np.asarray(img.convert("L"))
    return np.bincount(arr.ravel(), minlength=256)


def histogram_stats(hist: np.ndarray) -> Dict[str, float]:
    """Statistik dasar dari histogram: rata-rata, median, simpangan baku, min, max."""
    bins = np.arange(256)
    total = float(hist.sum())
    if total == 0:
        return {"mean": 0.0, "median": 0.0, "std": 0.0, "min": 0, "max": 0}
    mean = float((bins * hist).sum() / total)
    std = float(np.sqrt((((bins - mean) ** 2) * hist).sum() / total))
    median = int(np.searchsorted(np.cumsum(hist), total / 2.0))
    nz = np.nonzero(hist)[0]
    return {"mean": mean, "median": median, "std": std, "min": int(nz[0]), "max": int(nz[-1])}


# ==========================================================================
# Pembuatan figure Matplotlib
# ==========================================================================
def _style_axes(ax, title: str = "") -> None:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    ax.set_xlim(0, 255)
    ax.set_xticks([0, 64, 128, 192, 255])
    if title:
        ax.set_title(title, color=TEXT, fontsize=10, pad=6)


def _stats_text(ax, stats: Dict[str, float], color: str = TEXT) -> None:
    ax.text(
        0.98, 0.95,
        f"μ = {stats['mean']:.1f}\nσ = {stats['std']:.1f}\nmedian = {stats['median']}\n"
        f"min–max = {stats['min']}–{stats['max']}",
        transform=ax.transAxes, ha="right", va="top", fontsize=8, color=color,
        bbox=dict(boxstyle="round,pad=0.35", fc=BG, ec=GRID, alpha=0.9),
    )


def build_rgb_figure(img: Image.Image, title: str = "Histogram RGB") -> Figure:
    """Figure histogram RGB: tumpang-tindih (atas) + tiap kanal terpisah (bawah)."""
    hists = compute_rgb_histogram(img)
    x = np.arange(256)
    fig = Figure(figsize=(10, 6.4), dpi=100, facecolor=BG)
    gs = fig.add_gridspec(
        2, 3, height_ratios=[1.25, 1], hspace=0.42, wspace=0.28,
        left=0.07, right=0.97, top=0.90, bottom=0.08,
    )
    fig.suptitle(title, color=TEXT, fontsize=13, fontweight="bold")

    ax = fig.add_subplot(gs[0, :])
    _style_axes(ax, "Gabungan kanal R, G, B")
    for name, h in hists.items():
        ax.fill_between(x, h, color=CH_COLORS[name], alpha=0.30, linewidth=0)
        ax.plot(x, h, color=CH_COLORS[name], linewidth=1.1, label=name)
    ax.set_ylabel("Jumlah piksel", color=MUTED, fontsize=9)
    ax.set_ylim(bottom=0)
    legend = ax.legend(loc="upper left", fontsize=8, facecolor=BG, edgecolor=GRID)
    for t in legend.get_texts():
        t.set_color(TEXT)

    for col, name in enumerate("RGB"):
        a = fig.add_subplot(gs[1, col])
        _style_axes(a, {"R": "Red", "G": "Green", "B": "Blue"}[name])
        a.bar(x, hists[name], width=1.0, color=CH_COLORS[name], alpha=0.9, linewidth=0)
        a.set_ylim(bottom=0)
        _stats_text(a, histogram_stats(hists[name]), CH_COLORS[name])
    return fig


def build_gray_figure(img: Image.Image, title: str = "Histogram Grayscale") -> Figure:
    """Figure histogram grayscale beserta statistiknya."""
    h = compute_gray_histogram(img)
    x = np.arange(256)
    fig = Figure(figsize=(10, 6.4), dpi=100, facecolor=BG)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.89, bottom=0.10)
    fig.suptitle(title, color=TEXT, fontsize=13, fontweight="bold")
    _style_axes(ax)
    ax.bar(x, h, width=1.0, color=GRAY_COLOR, alpha=0.95, linewidth=0)
    ax.set_xlabel("Intensitas (0 = hitam, 255 = putih)", color=MUTED, fontsize=9)
    ax.set_ylabel("Jumlah piksel", color=MUTED, fontsize=9)
    ax.set_ylim(bottom=0)
    _stats_text(ax, histogram_stats(h))
    return fig


# ==========================================================================
# Jendela Tkinter
# ==========================================================================
class HistogramWindow:
    """Jendela histogram. ``get_images`` mengembalikan {'Hasil': img, 'Asli': img}.

    Gambar dibaca ulang setiap kali di-render, sehingga tombol "Segarkan"
    selalu menampilkan keadaan terbaru.
    """

    _opened = 0  # penghitung jendela, untuk menggeser posisi jendela baru

    def __init__(self, parent, get_images: Callable[[], Dict[str, Image.Image]], mode: str = "rgb"):
        import tkinter as tk  # impor di sini agar modul ini tetap bisa dipakai tanpa Tk

        self._tk = tk
        self.get_images = get_images
        self.mode = mode if mode in ("rgb", "gray") else "rgb"

        self.win = tk.Toplevel(parent)
        self.win.title("Histogram RGB" if self.mode == "rgb" else "Histogram Grayscale")
        self.win.configure(bg=BG)
        self.win.minsize(700, 520)
        # letakkan di tengah jendela utama, sedikit bergeser agar beberapa jendela tidak menumpuk
        parent.update_idletasks()
        offset = 28 * (HistogramWindow._opened % 5)
        HistogramWindow._opened += 1
        w, h = 960, 700
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - w) // 2) + offset
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - h) // 3) + offset
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.fig = None

        bar = tk.Frame(self.win, bg=BG)
        bar.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(bar, text="Sumber:", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")
        self.source = tk.StringVar(value="Hasil")
        for label in ("Hasil", "Asli"):
            tk.Radiobutton(
                bar, text=label, value=label, variable=self.source, command=self.render,
                bg=BG, fg=TEXT, selectcolor=PANEL, activebackground=BG, activeforeground=TEXT,
                font=("Segoe UI", 10), highlightthickness=0, bd=0,
            ).pack(side="left", padx=8)
        btn = dict(relief="flat", bd=0, padx=14, pady=4, cursor="hand2", font=("Segoe UI", 9, "bold"),
                   fg="white", activeforeground="white")
        tk.Button(bar, text="Segarkan", command=self.render, bg="#3b82f6",
                  activebackground="#60a5fa", **btn).pack(side="right")
        tk.Button(bar, text="Simpan PNG…", command=self.save_png, bg="#17233f",
                  activebackground="#22335c", **btn).pack(side="right", padx=8)

        self.body = tk.Frame(self.win, bg=BG)
        self.body.pack(fill="both", expand=True, padx=8, pady=8)
        self._canvas_widget = None
        self._canvas = None
        self.render()

    def save_png(self) -> None:
        """Simpan histogram yang sedang tampil sebagai file PNG."""
        from tkinter import filedialog, messagebox

        if self.fig is None:
            return
        path = filedialog.asksaveasfilename(
            parent=self.win, title="Simpan histogram", defaultextension=".png",
            initialfile=f"histogram_{self.mode}.png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        try:
            self.fig.savefig(path, facecolor=BG, dpi=150)
        except Exception as exc:
            messagebox.showerror("Simpan histogram", f"Gagal menyimpan:\n{exc}", parent=self.win)

    def render(self) -> None:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        images = self.get_images()
        img = images.get(self.source.get()) or next(iter(images.values()))
        label = self.source.get()
        if self.mode == "rgb":
            fig = build_rgb_figure(img, f"Histogram RGB — gambar {label}")
        else:
            fig = build_gray_figure(img, f"Histogram Grayscale — gambar {label}")

        if self._canvas_widget is not None:
            self._canvas_widget.destroy()

        self.fig = fig
        self._canvas = FigureCanvasTkAgg(fig, master=self.body)
        self._canvas_widget = self._canvas.get_tk_widget()
        self._canvas_widget.configure(bg=BG, highlightthickness=0)
        self._canvas_widget.pack(fill="both", expand=True)
        self._canvas.draw()

    def focus(self) -> None:
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()
