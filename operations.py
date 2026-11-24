"""
operations.py
=============
Kumpulan operasi pengolahan citra untuk Image Processing Studio.
Sesuai Menu Structure Panduan PCD (Pengolahan Citra Digital).

Struktur Kategori:
1. File (I/O, Validasi, Info)
2. Basic Ops:
   - Negative
   - Arithmetic (Add, Substract, Multiply, Divide)
   - Boolean (NOT, AND, OR, XOR)
   - Geometrics (Translation, Rotation, Zooming, Flipping, Cropping)
   - Thresholding
   - Convolution (3x3 Matrix, Custom Kernel, Soal 1-8-0)
   - Fourier Transform (FFT 2D Magnitude Spectrum)
   - Colouring (Binary, Grayscale, RGB, HSV, CMY, YUV, YIQ, Pseudo)
3. Enhancement:
   - Brightness & Contrast
   - Hist. Equalization
   - Smoothing (Spatial: Lowpass, Median | Frequency: ILPF, BLPF)
   - Sharpening (Spatial: Highpass, Highboost | Frequency: IHPF, BHPF)
   - Geometrics Correction
4. Noise:
   - Gaussian, Rayleigh, Erlang (Gamma), Exponential, Uniform, Impulse (Salt & Pepper)
5. Edge Detection:
   - 1'st Differential Gradient (Sobel, Prewitt, Robert)
   - 2'nd Differential Gradient (Laplacian, LoG, Canny)
   - Compass (Kirsch 8-arah)
6. Segmentation:
   - Global Thresholding, Otsu Thresholding, Adaptive Thresholding,
     K-Means Clustering, Region Growing, Watershed
"""
from __future__ import annotations

import io
import math
import os
from typing import Dict, List, Optional, Tuple, Union

import matplotlib as mpl
import numpy as np
from PIL import Image, ImageFilter, ImageOps

# --------------------------------------------------------------------------
# Kompatibilitas versi Pillow (konstanta resampling / transpose)
# --------------------------------------------------------------------------
try:
    LANCZOS = Image.Resampling.LANCZOS
    BICUBIC = Image.Resampling.BICUBIC
    BILINEAR = Image.Resampling.BILINEAR
    NEAREST = Image.Resampling.NEAREST
    _ROT_90 = Image.Transpose.ROTATE_90
    _ROT_180 = Image.Transpose.ROTATE_180
    _ROT_270 = Image.Transpose.ROTATE_270
except AttributeError:
    LANCZOS, BICUBIC, BILINEAR, NEAREST = Image.LANCZOS, Image.BICUBIC, Image.BILINEAR, Image.NEAREST
    _ROT_90, _ROT_180, _ROT_270 = Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270

MAX_DIMENSION = 20000


# ==========================================================================
# Helper umum I/O & Konversi
# ==========================================================================
def ensure_rgb(img: Image.Image) -> Image.Image:
    """Kembalikan salinan gambar dalam mode RGB."""
    if img.mode == "RGB":
        return img.copy()
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return img.convert("RGB")


def _to_array(img: Image.Image) -> np.ndarray:
    """Gambar -> array uint8 (H, W, 3)."""
    return np.asarray(img if img.mode == "RGB" else ensure_rgb(img))


def _from_array(arr: np.ndarray) -> Image.Image:
    """Array angka -> gambar RGB (nilai dipotong ke rentang 0..255)."""
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def load_image(path: str) -> Tuple[Image.Image, Optional[str]]:
    """Buka file gambar. Mengembalikan (gambar RGB, nama format asli)."""
    with Image.open(path) as im:
        fmt = im.format
        im = ImageOps.exif_transpose(im)
        im.load()
        rgb = ensure_rgb(im)
    return rgb, fmt


def save_image(img: Image.Image, path: str) -> int:
    """Simpan gambar ke path (format ditentukan dari ekstensi)."""
    ext = os.path.splitext(path)[1].lower()
    kwargs = {}
    if ext in (".jpg", ".jpeg"):
        kwargs = {"quality": 95, "optimize": True}
    elif ext == ".webp":
        kwargs = {"quality": 95}
    ensure_rgb(img).save(path, **kwargs)
    return os.path.getsize(path)


def format_bytes(n: float) -> str:
    """Format ukuran byte ke satuan yang mudah dibaca."""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{int(n)} B" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} GB"


def normalize_format(fmt: Optional[str]) -> str:
    """Nama format -> format standar Pillow."""
    f = (fmt or "PNG").upper()
    if f in ("JPG", "MPO"):
        f = "JPEG"
    return f if f in ("PNG", "JPEG", "BMP", "TIFF", "WEBP") else "PNG"


def estimate_file_size(img: Image.Image, fmt: Optional[str] = "PNG") -> int:
    """Perkiraan ukuran file (byte) gambar."""
    fmt = normalize_format(fmt)
    buf = io.BytesIO()
    kwargs = {"quality": 95} if fmt in ("JPEG", "WEBP") else {}
    ensure_rgb(img).save(buf, format=fmt, **kwargs)
    return buf.tell()


def get_image_info(
    img: Image.Image,
    path: Optional[str] = None,
    fmt: Optional[str] = None,
) -> Dict[str, object]:
    """Ringkasan informasi citra."""
    width, height = img.size
    if path and os.path.isfile(path):
        size_bytes = os.path.getsize(path)
        estimated = False
    else:
        size_bytes = estimate_file_size(img, fmt)
        estimated = True
    return {
        "width": width,
        "height": height,
        "resolution": f"{width} × {height} px",
        "megapixels": round(width * height / 1_000_000, 2),
        "format": normalize_format(fmt) if fmt else "-",
        "mode": img.mode,
        "file_size": size_bytes,
        "file_size_text": ("≈ " if estimated else "") + format_bytes(size_bytes),
    }


# ==========================================================================
# 1. BASIC OPS: Geometrics (Resize, Crop, Rotate, Flip, Translation, Zoom)
# ==========================================================================
def validate_resize(width, height) -> Tuple[int, int]:
    try:
        w, h = int(width), int(height)
    except (TypeError, ValueError):
        raise ValueError("Lebar dan tinggi harus berupa bilangan bulat.")
    if w < 1 or h < 1:
        raise ValueError("Lebar dan tinggi minimal 1 piksel.")
    if w > MAX_DIMENSION or h > MAX_DIMENSION:
        raise ValueError(f"Ukuran maksimum adalah {MAX_DIMENSION} piksel per sisi.")
    return w, h


def resize_image(img: Image.Image, width: int, height: int) -> Image.Image:
    w, h = validate_resize(width, height)
    return ensure_rgb(img).resize((w, h), LANCZOS)


def validate_crop_box(box, size) -> Tuple[int, int, int, int]:
    try:
        left, top, right, bottom = (int(v) for v in box)
    except (TypeError, ValueError):
        raise ValueError("Koordinat crop harus berupa bilangan bulat.")
    w, h = size
    if left < 0 or top < 0 or right > w or bottom > h:
        raise ValueError(f"Area crop harus berada di dalam gambar (0,0) – ({w},{h}).")
    if right - left < 1 or bottom - top < 1:
        raise ValueError("Area crop tidak valid: Kanan harus > Kiri dan Bawah harus > Atas.")
    return left, top, right, bottom


def crop_image(img: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    box = validate_crop_box((left, top, right, bottom), img.size)
    return ensure_rgb(img).crop(box)


def rotate_image(img: Image.Image, angle: float, expand: bool = True) -> Image.Image:
    try:
        angle = float(angle)
    except (TypeError, ValueError):
        raise ValueError("Sudut rotasi harus berupa angka.")
    src = ensure_rgb(img)
    a = angle % 360
    if a == 0:
        return src
    exact = {90: _ROT_270, 180: _ROT_180, 270: _ROT_90}
    if a in exact:
        return src.transpose(exact[a])
    return src.rotate(-angle, resample=BICUBIC, expand=expand, fillcolor=(0, 0, 0))


def flip_image(img: Image.Image, mode: str = "horizontal") -> Image.Image:
    src = ensure_rgb(img)
    mode = (mode or "").lower()
    if mode in ("horizontal", "h"):
        return ImageOps.mirror(src)
    if mode in ("vertical", "v"):
        return ImageOps.flip(src)
    raise ValueError("Mode flip harus 'horizontal' atau 'vertical'.")


def translate_image(img: Image.Image, dx: int, dy: int) -> Image.Image:
    """Translasi geometri citra sejauh (dx, dy) piksel."""
    src = ensure_rgb(img)
    w, h = src.size
    out = Image.new("RGB", (w, h), (0, 0, 0))
    out.paste(src, (int(dx), int(dy)))
    return out


def zoom_image(img: Image.Image, factor: float) -> Image.Image:
    """Zooming citra dengan faktor pengali (mis. 1.5 = 150%, 0.5 = 50%)."""
    f = float(factor)
    if f <= 0.05 or f > 10.0:
        raise ValueError("Faktor zoom harus antara 0.05× dan 10.0×.")
    src = ensure_rgb(img)
    nw = max(1, int(round(src.width * f)))
    nh = max(1, int(round(src.height * f)))
    resample = LANCZOS if f < 1.0 else BICUBIC
    return src.resize((nw, nh), resample)


# ==========================================================================
# 2. BASIC OPS: Arithmetic & Boolean
# ==========================================================================
def arithmetic_op(
    img: Image.Image,
    op: str,
    scalar: float = 0.0,
    other_img: Optional[Image.Image] = None,
) -> Image.Image:
    """Operasi Aritmatika Citra: Add (+), Substract (-), Multiply (*), Divide (/)."""
    arr1 = _to_array(img).astype(np.float32)
    op = op.lower().strip()

    if other_img is not None:
        other_resized = other_img.resize(img.size, LANCZOS)
        arr2 = _to_array(other_resized).astype(np.float32)
    else:
        arr2 = float(scalar)

    if op in ("add", "+"):
        res = arr1 + arr2
    elif op in ("substract", "sub", "-"):
        res = arr1 - arr2
    elif op in ("multiply", "mul", "*"):
        if other_img is not None:
            res = (arr1 * arr2) / 255.0
        else:
            res = arr1 * arr2
    elif op in ("divide", "div", "/"):
        if other_img is not None:
            res = (arr1 / (arr2 + 1.0)) * 255.0
        else:
            val = float(scalar) if scalar != 0 else 1.0
            res = arr1 / val
    else:
        raise ValueError(f"Operasi aritmatika '{op}' tidak dikenal.")

    return _from_array(res)


def boolean_op(
    img: Image.Image,
    op: str,
    mask_val: int = 255,
    other_img: Optional[Image.Image] = None,
) -> Image.Image:
    """Operasi Boolean Citra: NOT, AND, OR, XOR."""
    arr1 = _to_array(img)
    op = op.lower().strip()

    if op == "not":
        return Image.fromarray(255 - arr1)

    if other_img is not None:
        other_resized = other_img.resize(img.size, LANCZOS)
        arr2 = _to_array(other_resized)
    else:
        arr2 = np.uint8(np.clip(mask_val, 0, 255))

    if op == "and":
        res = arr1 & arr2
    elif op == "or":
        res = arr1 | arr2
    elif op == "xor":
        res = arr1 ^ arr2
    else:
        raise ValueError(f"Operasi boolean '{op}' tidak dikenal.")

    return Image.fromarray(res)


# ==========================================================================
# 3. BASIC OPS: Negative, Thresholding, Convolution, Fourier Transform
# ==========================================================================
def negative(img: Image.Image) -> Image.Image:
    """Citra negatif: piksel' = 255 - piksel."""
    return Image.fromarray(255 - _to_array(img))


def threshold(img: Image.Image, value: int = 128) -> Image.Image:
    """Thresholding biner: piksel gray >= value -> putih, selain itu hitam."""
    t = int(value)
    if not 0 <= t <= 255:
        raise ValueError("Nilai threshold harus di antara 0 dan 255.")
    gray = np.asarray(ensure_rgb(img).convert("L"))
    binary = np.where(gray >= t, 255, 0).astype(np.uint8)
    return Image.fromarray(np.stack([binary] * 3, axis=-1))


def convolve_3x3(arr_2d: np.ndarray, k: np.ndarray, divisor: float = 1.0, offset: float = 0.0) -> np.ndarray:
    """Konvolusi 2D cepat untuk kernel 3x3 dengan padding reflect."""
    padded = np.pad(arr_2d.astype(np.float32), 1, mode="reflect")
    res = (
        k[0, 0] * padded[:-2, :-2] + k[0, 1] * padded[:-2, 1:-1] + k[0, 2] * padded[:-2, 2:] +
        k[1, 0] * padded[1:-1, :-2] + k[1, 1] * padded[1:-1, 1:-1] + k[1, 2] * padded[1:-1, 2:] +
        k[2, 0] * padded[2:, :-2] + k[2, 1] * padded[2:, 1:-1] + k[2, 2] * padded[2:, 2:]
    )
    if divisor != 0:
        res = res / divisor
    return np.clip(res + offset, 0, 255)


def convolve_matrix(
    img: Image.Image,
    kernel: Union[np.ndarray, List[List[float]]],
    divisor: Optional[float] = None,
    offset: float = 0.0,
) -> Image.Image:
    """Konvolusi matriks citra (mis. kernel 3x3 dari Halaman 2: 1 2 3 / 4 5 6 / 7 8 0)."""
    k = np.array(kernel, dtype=np.float32)
    if k.shape != (3, 3):
        raise ValueError("Kernel konvolusi harus berukuran 3×3.")

    if divisor is None:
        k_sum = float(np.sum(k))
        divisor = k_sum if k_sum != 0 else 1.0

    arr = _to_array(img)
    channels = []
    for c in range(3):
        conv_c = convolve_3x3(arr[..., c], k, float(divisor), float(offset))
        channels.append(conv_c.astype(np.uint8))

    return Image.fromarray(np.stack(channels, axis=-1))


def fourier_transform(img: Image.Image) -> Image.Image:
    """Transformasi Fourier 2D (FFT Magnitude Spectrum dalam skala logaritmik)."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    F = np.fft.fftshift(np.fft.fft2(gray))
    magnitude = np.abs(F)
    spectrum = np.log1p(magnitude)
    s_min, s_max = spectrum.min(), spectrum.max()
    if s_max > s_min:
        norm = (spectrum - s_min) / (s_max - s_min) * 255.0
    else:
        norm = np.zeros_like(spectrum)
    out = np.clip(norm, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([out] * 3, axis=-1))


# ==========================================================================
# 4. BASIC OPS: Colouring (Binary, Grayscale, RGB, HSV, CMY, YUV, YIQ, Pseudo)
# ==========================================================================
_CHANNEL_INDEX = {"R": 0, "G": 1, "B": 2, "RED": 0, "GREEN": 1, "BLUE": 2}


def channel_view(img: Image.Image, channel: str) -> Image.Image:
    """Tampilkan kanal warna RGB tunggal."""
    idx = _CHANNEL_INDEX.get(str(channel).upper())
    if idx is None:
        raise ValueError("Kanal harus 'R', 'G', atau 'B'.")
    arr = _to_array(img)
    out = np.zeros_like(arr)
    out[..., idx] = arr[..., idx]
    return Image.fromarray(out)


def adjust_rgb(img: Image.Image, r: float = 0, g: float = 0, b: float = 0) -> Image.Image:
    offsets = np.array([r, g, b], dtype=np.float32) * 2.55
    return _from_array(_to_array(img).astype(np.float32) + offsets)


def to_binary(img: Image.Image, value: int = 128) -> Image.Image:
    """Citra biner (hitam-putih)."""
    return threshold(img, value)


def to_grayscale(img: Image.Image) -> Image.Image:
    """Citra grayscale ITU-R 601 (0.299 R + 0.587 G + 0.114 B)."""
    return ensure_rgb(img).convert("L").convert("RGB")


def to_hsv(img: Image.Image) -> Image.Image:
    """Konversi representasi ruang warna HSV."""
    return ensure_rgb(img).convert("HSV").convert("RGB")


def to_cmy(img: Image.Image) -> Image.Image:
    """Konversi ke ruang warna CMY (Cyan, Magenta, Yellow = 255 - RGB)."""
    arr = _to_array(img)
    cmy = 255 - arr
    return Image.fromarray(cmy)


def to_yuv(img: Image.Image) -> Image.Image:
    """Konversi ke ruang warna YUV (standar PAL/NTSC)."""
    arr = _to_array(img).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = -0.14713 * r - 0.28886 * g + 0.436 * b + 128.0
    v = 0.615 * r - 0.51499 * g - 0.10001 * b + 128.0
    yuv = np.stack([y, u, v], axis=-1)
    return _from_array(yuv)


def to_yiq(img: Image.Image) -> Image.Image:
    """Konversi ke ruang warna YIQ (standar NTSC)."""
    arr = _to_array(img).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    i = 0.595716 * r - 0.274453 * g - 0.321263 * b + 128.0
    q = 0.211456 * r - 0.522591 * g + 0.311135 * b + 128.0
    yiq = np.stack([y, i, q], axis=-1)
    return _from_array(yiq)


def to_pseudocolor(img: Image.Image, colormap: str = "jet") -> Image.Image:
    """Pemberian warna semu (Pseudocolor) menggunakan colormap Matplotlib."""
    gray = np.asarray(ensure_rgb(img).convert("L")) / 255.0
    cmap_name = colormap.lower().strip()
    try:
        cmap = mpl.colormaps[cmap_name]
    except KeyError:
        cmap = mpl.colormaps["jet"]
    rgba = cmap(gray)
    rgb = (rgba[..., :3] * 255.0).astype(np.uint8)
    return Image.fromarray(rgb)


# ==========================================================================
# 5. ENHANCEMENT: Brightness, Contrast, Hist. Equalization, Smoothing, Sharpening
# ==========================================================================
def adjust_brightness(img: Image.Image, value: float) -> Image.Image:
    if not -100 <= float(value) <= 100:
        raise ValueError("Nilai brightness harus di antara -100 dan 100.")
    return _from_array(_to_array(img).astype(np.float32) + float(value) * 2.55)


def adjust_contrast(img: Image.Image, value: float) -> Image.Image:
    if not -100 <= float(value) <= 100:
        raise ValueError("Nilai contrast harus di antara -100 dan 100.")
    c = float(value) * 2.0
    factor = (259.0 * (c + 255.0)) / (255.0 * (259.0 - c))
    arr = _to_array(img).astype(np.float32)
    return _from_array(factor * (arr - 128.0) + 128.0)


def histogram_equalization(img: Image.Image) -> Image.Image:
    """Pemerataan Histogram (Histogram Equalization) pada kanal intensitas V."""
    src = ensure_rgb(img)
    hsv = src.convert("HSV")
    h, s, v = hsv.split()
    v_arr = np.asarray(v)

    hist, _ = np.histogram(v_arr.flatten(), 256, [0, 256])
    cdf = hist.cumsum()
    cdf_masked = np.ma.masked_equal(cdf, 0)
    cdf_m = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
    cdf_final = np.ma.filled(cdf_m, 0).astype(np.uint8)

    v_eq = cdf_final[v_arr]
    v_img = Image.fromarray(v_eq, mode="L")
    return Image.merge("HSV", (h, s, v_img)).convert("RGB")


# ---- Smoothing Spatial
def spatial_lowpass(img: Image.Image, radius: float = 2.0) -> Image.Image:
    """Lowpass Filtering dalam domain spasial (Gaussian Lowpass)."""
    r = max(0.1, float(radius))
    return ensure_rgb(img).filter(ImageFilter.GaussianBlur(r))


def spatial_median(img: Image.Image, size: int = 3) -> Image.Image:
    """Median Filtering dalam domain spasial (efektif menghilangkan impulse noise)."""
    s = int(size)
    if s % 2 == 0:
        s += 1
    s = max(3, min(15, s))
    return ensure_rgb(img).filter(ImageFilter.MedianFilter(size=s))


# ---- Filter Domain Frekuensi Helper
def _freq_filter(img: Image.Image, filter_mask_fn) -> Image.Image:
    arr = _to_array(img).astype(np.float32)
    h, w, c = arr.shape
    u = np.arange(h) - (h / 2.0)
    v = np.arange(w) - (w / 2.0)
    U, V = np.meshgrid(u, v, indexing="ij")
    D = np.sqrt(U**2 + V**2)
    H = filter_mask_fn(D)

    out = np.zeros_like(arr)
    for ch in range(c):
        F = np.fft.fftshift(np.fft.fft2(arr[:, :, ch]))
        G = F * H
        filtered = np.fft.ifft2(np.fft.ifftshift(G))
        out[:, :, ch] = np.abs(filtered)
    return _from_array(out)


# ---- Smoothing Frequency
def freq_ilpf(img: Image.Image, d0: float = 50.0) -> Image.Image:
    """Ideal Lowpass Filter (ILPF) dalam domain frekuensi."""
    cutoff = max(1.0, float(d0))
    return _freq_filter(img, lambda D: (D <= cutoff).astype(np.float32))


def freq_blpf(img: Image.Image, d0: float = 50.0, n: int = 2) -> Image.Image:
    """Butterworth Lowpass Filter (BLPF) dalam domain frekuensi."""
    cutoff = max(1.0, float(d0))
    order = max(1, int(n))
    return _freq_filter(img, lambda D: 1.0 / (1.0 + (D / cutoff) ** (2 * order)))


# ---- Sharpening Spatial
_HIGHPASS_KERNEL = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)


def spatial_highpass(img: Image.Image) -> Image.Image:
    """Highpass Filtering dalam domain spasial."""
    return convolve_matrix(img, _HIGHPASS_KERNEL, divisor=1.0, offset=0.0)


def spatial_highboost(img: Image.Image, a: float = 1.5) -> Image.Image:
    """Highboost Filtering dalam domain spasial: Hasil = A·Original - Lowpass."""
    boost = max(1.0, float(a))
    src = _to_array(img).astype(np.float32)
    lowpass = _to_array(spatial_lowpass(img, radius=2.0)).astype(np.float32)
    highboost = boost * src - lowpass
    return _from_array(highboost)


# ---- Sharpening Frequency
def freq_ihpf(img: Image.Image, d0: float = 50.0) -> Image.Image:
    """Ideal Highpass Filter (IHPF) dalam domain frekuensi."""
    cutoff = max(1.0, float(d0))
    return _freq_filter(img, lambda D: (D > cutoff).astype(np.float32))


def freq_bhpf(img: Image.Image, d0: float = 50.0, n: int = 2) -> Image.Image:
    """Butterworth Highpass Filter (BHPF) dalam domain frekuensi."""
    cutoff = max(1.0, float(d0))
    order = max(1, int(n))
    return _freq_filter(img, lambda D: 1.0 / (1.0 + (cutoff / np.maximum(D, 1e-5)) ** (2 * order)))


# ---- Geometrics Correction
def geometrics_correction(
    img: Image.Image,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    barrel: float = 0.0,
) -> Image.Image:
    """Koreksi geometris (Shear koreksi kemiringan perspektif & distorsi lensa)."""
    src = ensure_rgb(img)
    w, h = src.size

    # Koreksi shear jika ada
    if abs(shear_x) > 1e-4 or abs(shear_y) > 1e-4:
        # Affine matrix: x' = x + sx * y, y' = sy * x + y
        sx, sy = float(shear_x) / 100.0, float(shear_y) / 100.0
        matrix = (1, sx, 0, sy, 1, 0)
        src = src.transform((w, h), Image.Transform.AFFINE, matrix, resample=BICUBIC)

    # Koreksi distorsi lensa radial (barrel / pincushion) jika ada
    k = float(barrel) / 100.0
    if abs(k) > 1e-4:
        arr = np.asarray(src)
        yc, xc = h / 2.0, w / 2.0
        y, x = np.indices((h, w), dtype=np.float32)
        rn_x = (x - xc) / xc
        rn_y = (y - yc) / yc
        r2 = rn_x**2 + rn_y**2
        factor = 1.0 + k * r2

        map_x = np.clip(xc + rn_x * factor * xc, 0, w - 1).astype(int)
        map_y = np.clip(yc + rn_y * factor * yc, 0, h - 1).astype(int)
        corrected = arr[map_y, map_x]
        return Image.fromarray(corrected)

    return src


# ==========================================================================
# 6. NOISE: Gaussian, Rayleigh, Erlang, Exponential, Uniform, Impulse
# ==========================================================================
def add_gaussian_noise(img: Image.Image, mean: float = 0.0, std: float = 25.0) -> Image.Image:
    """Noise Gaussian: N(mean, std²)."""
    arr = _to_array(img).astype(np.float32)
    noise = np.random.normal(float(mean), float(std), arr.shape)
    return _from_array(arr + noise)


def add_rayleigh_noise(img: Image.Image, scale: float = 20.0) -> Image.Image:
    """Noise Rayleigh: P(g) = (2/b)(g-a)e^{-(g-a)²/b}."""
    arr = _to_array(img).astype(np.float32)
    s = max(1.0, float(scale))
    noise = np.random.rayleigh(s, arr.shape) - (s * np.sqrt(np.pi / 2))
    return _from_array(arr + noise)


def add_erlang_noise(img: Image.Image, a: int = 2, b: float = 15.0) -> Image.Image:
    """Noise Erlang (Gamma): shape=a, scale=b."""
    arr = _to_array(img).astype(np.float32)
    shape_param = max(1, int(a))
    scale_param = max(1.0, float(b))
    noise = np.random.gamma(shape_param, scale_param, arr.shape) - (shape_param * scale_param)
    return _from_array(arr + noise)


def add_exponential_noise(img: Image.Image, scale: float = 20.0) -> Image.Image:
    """Noise Eksponensial: P(g) = a e^{-ag}."""
    arr = _to_array(img).astype(np.float32)
    s = max(1.0, float(scale))
    noise = np.random.exponential(s, arr.shape) - s
    return _from_array(arr + noise)


def add_uniform_noise(img: Image.Image, low: float = -30.0, high: float = 30.0) -> Image.Image:
    """Noise Seragam (Uniform): U(low, high)."""
    arr = _to_array(img).astype(np.float32)
    noise = np.random.uniform(float(low), float(high), arr.shape)
    return _from_array(arr + noise)


def add_impulse_noise(img: Image.Image, amount: float = 0.05) -> Image.Image:
    """Noise Impuls (Salt & Pepper): piksel hitam & putih acak."""
    p = max(0.001, min(0.99, float(amount)))
    arr = _to_array(img).copy()
    num_salt = np.ceil(p * arr.shape[0] * arr.shape[1] * 0.5)
    num_pepper = np.ceil(p * arr.shape[0] * arr.shape[1] * 0.5)

    # Salt (Putih 255)
    coords_salt = [np.random.randint(0, i - 1, int(num_salt)) for i in arr.shape[:2]]
    arr[tuple(coords_salt)] = 255

    # Pepper (Hitam 0)
    coords_pep = [np.random.randint(0, i - 1, int(num_pepper)) for i in arr.shape[:2]]
    arr[tuple(coords_pep)] = 0

    return Image.fromarray(arr)


# ==========================================================================
# 7. EDGE DETECTION: 1st Diff (Sobel, Prewitt, Robert), 2nd Diff (Laplacian, LoG, Canny), Compass
# ==========================================================================
def _gradient_magnitude(arr_gray: np.ndarray, kx: np.ndarray, ky: np.ndarray) -> np.ndarray:
    gx = convolve_3x3(arr_gray, kx, divisor=1.0, offset=0.0)
    gy = convolve_3x3(arr_gray, ky, divisor=1.0, offset=0.0)
    return np.hypot(gx, gy)


# ---- 1'st Differential Gradient
def sobel_edge(img: Image.Image) -> Image.Image:
    """Deteksi Tepi Sobel (Gradien Ordo 1)."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    mag = _gradient_magnitude(gray, kx, ky)
    res = np.clip(mag, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([res] * 3, axis=-1))


def prewitt_edge(img: Image.Image) -> Image.Image:
    """Deteksi Tepi Prewitt (Gradien Ordo 1)."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    mag = _gradient_magnitude(gray, kx, ky)
    res = np.clip(mag, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([res] * 3, axis=-1))


def roberts_edge(img: Image.Image) -> Image.Image:
    """Deteksi Tepi Roberts Cross (Gradien Ordo 1)."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    # Roberts Cross 2x2
    p = np.pad(gray, ((0, 1), (0, 1)), mode="reflect")
    gx = p[:-1, :-1] - p[1:, 1:]
    gy = p[:-1, 1:] - p[1:, :-1]
    mag = np.hypot(gx, gy)
    res = np.clip(mag, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([res] * 3, axis=-1))


# ---- 2'nd Differential Gradient
def laplacian_edge(img: Image.Image) -> Image.Image:
    """Deteksi Tepi Laplacian (Gradien Ordo 2)."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    lap = np.abs(convolve_3x3(gray, k, divisor=1.0, offset=0.0))
    res = np.clip(lap, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([res] * 3, axis=-1))


def log_edge(img: Image.Image, sigma: float = 1.4) -> Image.Image:
    """Laplacian of Gaussian (LoG): Gaussian Smoothing diikuti Laplacian."""
    blurred = ensure_rgb(img).filter(ImageFilter.GaussianBlur(float(sigma)))
    return laplacian_edge(blurred)


def canny_edge(img: Image.Image, low: float = 50.0, high: float = 150.0) -> Image.Image:
    """Deteksi Tepi Canny (Optimal edge detection dengan Non-Maximum Suppression)."""
    blurred = np.asarray(ensure_rgb(img).convert("L").filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32)
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)

    p = np.pad(blurred, 1, mode="reflect")
    gx = (kx[0, 0] * p[:-2, :-2] + kx[0, 2] * p[:-2, 2:] +
          kx[1, 0] * p[1:-1, :-2] + kx[1, 2] * p[1:-1, 2:] +
          kx[2, 0] * p[2:, :-2] + kx[2, 2] * p[2:, 2:])
    gy = (ky[0, 0] * p[:-2, :-2] + ky[0, 1] * p[:-2, 1:-1] + ky[0, 2] * p[:-2, 2:] +
          ky[2, 0] * p[2:, :-2] + ky[2, 1] * p[2:, 1:-1] + ky[2, 2] * p[2:, 2:])

    mag = np.hypot(gx, gy)
    ang = np.rad2deg(np.arctan2(gy, gx)) % 180
    nms = np.zeros_like(mag)
    h, w = mag.shape
    p_mag = np.pad(mag, 1, mode="constant")

    m0 = (ang < 22.5) | (ang >= 157.5)
    nms[m0] = np.where((mag[m0] >= p_mag[1:-1, :-2][m0]) & (mag[m0] >= p_mag[1:-1, 2:][m0]), mag[m0], 0)
    m45 = (ang >= 22.5) & (ang < 67.5)
    nms[m45] = np.where((mag[m45] >= p_mag[:-2, 2:][m45]) & (mag[m45] >= p_mag[2:, :-2][m45]), mag[m45], 0)
    m90 = (ang >= 67.5) & (ang < 112.5)
    nms[m90] = np.where((mag[m90] >= p_mag[:-2, 1:-1][m90]) & (mag[m90] >= p_mag[2:, 1:-1][m90]), mag[m90], 0)
    m135 = (ang >= 112.5) & (ang < 157.5)
    nms[m135] = np.where((mag[m135] >= p_mag[:-2, :-2][m135]) & (mag[m135] >= p_mag[2:, 2:][m135]), mag[m135], 0)

    strong = nms >= float(high)
    weak = (nms >= float(low)) & (~strong)
    res = np.zeros((h, w), dtype=np.uint8)
    res[strong] = 255

    # Hysteresis tracking
    p_res = np.pad(res, 1, mode="constant")
    has_strong = (
        (p_res[:-2, :-2] == 255) | (p_res[:-2, 1:-1] == 255) | (p_res[:-2, 2:] == 255) |
        (p_res[1:-1, :-2] == 255) | (p_res[1:-1, 2:] == 255) |
        (p_res[2:, :-2] == 255) | (p_res[2:, 1:-1] == 255) | (p_res[2:, 2:] == 255)
    )
    res[weak & has_strong] = 255
    return Image.fromarray(np.stack([res] * 3, axis=-1))


# ---- Compass Edge Detection
_KIRSCH_KERNELS = [
    np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]], dtype=np.float32),      # N
    np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]], dtype=np.float32),     # NW
    np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]], dtype=np.float32),     # W
    np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]], dtype=np.float32),     # SW
    np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]], dtype=np.float32),     # S
    np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]], dtype=np.float32),     # SE
    np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]], dtype=np.float32),     # E
    np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]], dtype=np.float32),     # NE
]


def compass_edge(img: Image.Image) -> Image.Image:
    """Deteksi Tepi Compass (Operator Kirsch 8 Arah Mata Angin)."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    max_response = np.zeros_like(gray)
    for k in _KIRSCH_KERNELS:
        resp = np.abs(convolve_3x3(gray, k, divisor=1.0, offset=0.0))
        max_response = np.maximum(max_response, resp)
    res = np.clip(max_response, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([res] * 3, axis=-1))


# ==========================================================================
# 8. SEGMENTATION: Global Thresh, Otsu, Adaptive, K-Means, Region Growing, Watershed
# ==========================================================================
def segment_global_threshold(img: Image.Image, value: int = 128) -> Image.Image:
    """Segmentasi Thresholding Global."""
    return threshold(img, value)


def segment_otsu(img: Image.Image) -> Image.Image:
    """Segmentasi Otsu: Ambang batas otomatis yang memaksimalkan variansi antarkelas."""
    gray = np.asarray(ensure_rgb(img).convert("L"))
    hist, _ = np.histogram(gray.ravel(), bins=256, range=(0, 256))
    total = gray.size
    current_max, threshold_otsu = 0.0, 128
    weight_bg, sum_bg = 0, 0
    sum_total = np.dot(np.arange(256), hist)

    for t in range(256):
        weight_bg += hist[t]
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break
        sum_bg += t * hist[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        var_between = weight_bg * weight_fg * ((mean_bg - mean_fg) ** 2)
        if var_between > current_max:
            current_max = var_between
            threshold_otsu = t

    return threshold(img, threshold_otsu)


def segment_adaptive(img: Image.Image, block_size: int = 15, c: float = 2.0) -> Image.Image:
    """Segmentasi Thresholding Adaptif (Lokal)."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    bs = max(3, int(block_size) | 1)  # pastikan ganjil
    # Local mean menggunakan BoxBlur
    mean_im = ensure_rgb(img).convert("L").filter(ImageFilter.BoxBlur(bs // 2))
    local_mean = np.asarray(mean_im).astype(np.float32)
    binary = np.where(gray >= (local_mean - float(c)), 255, 0).astype(np.uint8)
    return Image.fromarray(np.stack([binary] * 3, axis=-1))


def segment_kmeans(img: Image.Image, k: int = 3, max_iter: int = 15) -> Image.Image:
    """Segmentasi K-Means Clustering pada ruang warna RGB."""
    k = max(2, min(8, int(k)))
    arr = _to_array(img)
    pixels = arr.reshape((-1, 3)).astype(np.float32)

    # Inisialisasi centroid acak
    np.random.seed(42)
    indices = np.random.choice(len(pixels), k, replace=False)
    centroids = pixels[indices]

    for _ in range(max_iter):
        # Hitung jarak Euclidean
        dists = np.linalg.norm(pixels[:, np.newaxis] - centroids, axis=2)
        labels = np.argmin(dists, axis=1)
        new_centroids = np.array([
            pixels[labels == i].mean(axis=0) if np.any(labels == i) else centroids[i]
            for i in range(k)
        ])
        if np.allclose(centroids, new_centroids, atol=1.0):
            break
        centroids = new_centroids

    segmented_pixels = centroids[labels].astype(np.uint8)
    return Image.fromarray(segmented_pixels.reshape(arr.shape))


def segment_region_growing(img: Image.Image, threshold: float = 20.0) -> Image.Image:
    """Segmentasi Region Growing berbasis benih di titik pusat citra."""
    gray = np.asarray(ensure_rgb(img).convert("L")).astype(np.float32)
    h, w = gray.shape
    segmented = np.zeros((h, w), dtype=np.uint8)
    visited = np.zeros((h, w), dtype=bool)

    seed_y, seed_x = h // 2, w // 2
    seed_val = gray[seed_y, seed_x]

    thresh = float(threshold)
    queue = [(seed_y, seed_x)]
    visited[seed_y, seed_x] = True

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        cy, cx = queue.pop()
        segmented[cy, cx] = 255

        for dy, dx in directions:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                visited[ny, nx] = True
                if abs(gray[ny, nx] - seed_val) <= thresh:
                    queue.append((ny, nx))

    return Image.fromarray(np.stack([segmented] * 3, axis=-1))


def segment_watershed(img: Image.Image) -> Image.Image:
    """Segmentasi Watershed menggunakan peta gradien citra."""
    gray = np.asarray(ensure_rgb(img).convert("L"))
    # Gradien dengan Sobel
    grad = np.asarray(sobel_edge(img).convert("L"))
    # Otsu threshold pada gradien sebagai batas watershed
    otsu_grad = np.asarray(segment_otsu(Image.fromarray(grad)).convert("L"))
    # Overlay kontur batas putih pada gambar asli
    src = _to_array(img).copy()
    src[otsu_grad == 255] = [255, 60, 60]  # Garis pemisah merah menyala
    return Image.fromarray(src)
