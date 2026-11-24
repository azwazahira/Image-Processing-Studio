# Panduan Penggunaan Lengkap (Tutorial) 📖
## Image Processing Studio — Tim Visionary (2026)

Selamat datang di panduan resmi penggunaan **Image Processing Studio**. Dokumen ini dirancang sebagai panduan komprehensif langkah demi langkah bagi mahasiswa, pengajar, maupun peneliti dalam mengoperasikan seluruh fitur pengolahan citra digital di aplikasi ini.

---

## 📑 Daftar Isi
1. [Memulai dan Mengenal Antarmuka](#1-memulai-dan-mengenal-antarmuka)
2. [Manajemen File dan Riwayat Operasi](#2-manajemen-file-dan-riwayat-operasi)
3. [Panduan Menu: Basic Ops (Operasi Dasar)](#3-panduan-menu-basic-ops-operasi-dasar)
4. [Panduan Menu: Enhancement (Perbaikan Kualitas Citra)](#4-panduan-menu-enhancement-perbaikan-kualitas-citra)
5. [Panduan Menu: Noise (Simulasi Gangguan Citra)](#5-panduan-menu-noise-simulasi-gangguan-citra)
6. [Panduan Menu: Edge Detection (Deteksi Tepi)](#6-panduan-menu-edge-detection-deteksi-tepi)
7. [Panduan Menu: Segmentation (Segmentasi Citra)](#7-panduan-menu-segmentation-segmentasi-citra)
8. [Panduan Analisis Histogram](#8-panduan-analisis-histogram)
9. [Studi Kasus Alur Kerja Praktikum PCD](#9-studi-kasus-alur-kerja-praktikum-pcd)
10. [Tips & Pemecahan Masalah (Troubleshooting)](#10-tips--pemecahan-masalah-troubleshooting)

---

## 1. Memulai dan Mengenal Antarmuka

### Menjalankan Aplikasi
Buka terminal (PowerShell atau Command Prompt) pada direktori proyek, lalu jalankan perintah:
```powershell
.\.venv\Scripts\python.exe main.py
```
*(atau jika menggunakan Python sistem: `python main.py`)*

### Bagian-Bagian Antarmuka
Antarmuka terbagi menjadi 4 area utama:
1. **Menu Bar (Atas)**: Akses cepat hierarkis ke 7 menu utama: `File`, `Basic Ops`, `Enhancement`, `Noise`, `Edge Detection`, `Segmentation`, dan `About`.
2. **Sidebar Navigasi (Kiri)**: Panel pintasan dengan tombol-tombol operasi yang dikelompokkan secara rapi dan dapat digulir (*scrollable*).
3. **Dual Preview Panel (Tengah)**:
   * **Panel Kiri (Gambar Asli)**: Menampilkan citra awal saat pertama kali dibuka. Citra ini bersifat *read-only* dan tidak pernah diubah.
   * **Panel Kanan (Hasil Pengolahan)**: Menampilkan citra hasil modifikasi setiap kali Anda menerapkan operasi. Dilengkapi indikator zoom dan resolusi di sudut kanan bawah.
4. **Kartu Metadata & Status Bar (Bawah)**:
   * **Kartu Gambar Asli**: Menampilkan nama file, resolusi, format, ukuran file, dan mode warna.
   * **Kartu Hasil Pengolahan**: Menampilkan resolusi hasil, format simpan, perkiraan ukuran file, serta riwayat operasi berurutan (misal: `Grayscale → Median Filter → Sobel`).
   * **Status Bar**: Menampilkan status aksi terkini, dimensi citra, serta indikator perubahan belum tersimpan.

---

## 2. Manajemen File dan Riwayat Operasi

### Membuka Gambar (Open)
1. Klik menu **File → Open…** atau tekan pintasan **<kbd>Ctrl</kbd> + <kbd>O</kbd>**.
2. Anda juga dapat mengklik tombol biru **"Buka Gambar"** di sudut kanan atas header.
3. Pilih file gambar di komputer Anda (format yang didukung: PNG, JPG, JPEG, BMP, TIFF, WebP, GIF).
4. Citra akan dimuat pada kedua panel (Asli dan Hasil) secara berdampingan.

### Menyimpan Hasil (Save & Save As)
* **Save (<kbd>Ctrl</kbd> + <kbd>S</kbd>)**: Jika file sudah pernah dibuka dari disk, perubahan akan langsung disimpan ke file tersebut.
* **Save As (<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>)**: Membuka dialog untuk memilih nama file baru, folder tujuan, dan ekstensi penyimpanan (`.png`, `.jpg`, `.bmp`, `.webp`, `.tif`).

### Membatalkan Operasi (Undo)
* Jika Anda salah memilih filter atau ingin kembali ke langkah sebelumnya, klik tombol **Undo** pada sidebar atau tekan **<kbd>Ctrl</kbd> + <kbd>Z</kbd>**.
* Aplikasi menyimpan histori hingga **20 langkah terakhir**.

### Mengembalikan ke Gambar Asli (Reset Asli)
* Klik **Reset Asli** di sidebar untuk mengembalikan citra hasil agar sama persis dengan citra asli. Operasi reset ini juga dapat dibatalkan dengan *Undo*.

### Keluar dari Aplikasi (Exit)
* Pilih menu **File → Exit** atau tekan **<kbd>Ctrl</kbd> + <kbd>Q</kbd>**. Jika ada perubahan yang belum disimpan, aplikasi akan menampilkan konfirmasi pengingat.

---

## 3. Panduan Menu: Basic Ops (Operasi Dasar)

Menu **Basic Ops** memuat operasi aljabar, geometri, binarisasi, konvolusi, dan spektrum frekuensi:

### 3.1 Negative (Citra Negatif)
* **Akses**: Menu `Basic Ops → Negative` atau tombol sidebar `Negative`.
* **Cara Kerja**: Membalikkan nilai intensitas setiap piksel: $\text{Piksel Baru} = 255 - \text{Piksel Lama}$.

### 3.2 Arithmetic (Operasi Aritmatika)
* **Akses**: Menu `Basic Ops → Arithmetic -->` (`Add`, `Substract`, `Multiply`, `Divide`).
* **Fitur Fleksibel**:
  * **Opsi 1 (Nilai Skalar / Slider)**: Menambahkan/mengurangi/mengalikan/membagi intensitas piksel dengan suatu angka konstan. Terdapat *live preview* real-time saat slider digeser.
  * **Opsi 2 (Dengan Citra Kedua)**: Klik *"Dengan Citra Kedua"*, lalu klik *"Pilih Gambar Kedua…"*. Citra kedua akan otomatis diselaraskan ukurannya, lalu dioperasikan secara piksel-per-piksel terhadap citra aktif.
* Klik **Terapkan** untuk mengonfirmasi.

### 3.3 Boolean (Operasi Logika Biner)
* **Akses**: Menu `Basic Ops → Boolean -->` (`NOT`, `AND`, `OR`, `XOR`).
* **NOT**: Langsung melakukan negasi bitwise pada citra aktif.
* **AND / OR / XOR**: Membuka dialog pilihan apakah ingin dioperasikan terhadap masker biner konstan ($0 \dots 255$) atau dipadukan secara logika bitwise dengan file citra kedua.

### 3.4 Geometrics (Transformasi Geometri)
* **Translation (Translasi)**: Menggeser citra secara spasial ke sumbu X (kiri/kanan) dan Y (atas/bawah). Area kosong diisi warna hitam.
* **Rotation (Rotasi)**: Memutar citra dari $-180^\circ$ s.d $+180^\circ$ dengan interpolasi Bicubic bebas gerigi.
* **Zooming (Penskalaan)**: Memperbesar atau memperkecil skala tampilan citra dari $10\%$ hingga $400\%$.
* **Flipping (Pembalikan)**: Membalikkan citra secara Horisontal (cermin kiri-kanan) atau Vertikal (atas-bawah).
* **Cropping (Pemotongan)**: Memasukkan koordinat batas kotak potong $(X_1, Y_1)$ untuk titik kiri-atas dan $(X_2, Y_2)$ untuk titik kanan-bawah.

### 3.5 Thresholding (Pengambangan Biner)
* Mengubah citra menjadi biner hitam-putih murni berdasarkan batas nilai intensitas $T$ ($0 \dots 255$).
* Geser slider ambang batas; piksel $\ge T$ akan menjadi putih ($255$), sedangkan piksel $< T$ menjadi hitam ($0$).

### 3.6 Convolution (Konvolusi Matriks 3×3)
* **Akses**: Menu `Basic Ops → Convolution`.
* **Antarmuka Matriks 3×3**:
  Menyediakan 9 kotak input angka untuk nilai bobot kernel:
  $$\begin{bmatrix} K_{00} & K_{01} & K_{02} \\ K_{10} & K_{11} & K_{12} \\ K_{20} & K_{21} & K_{22} \end{bmatrix}$$
* **Template Soal Halaman 2**:
  Secara default terisi matriks template dari halaman 2 dokumen tugas:
  $$\begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 0 \end{bmatrix}$$
* **Pilihan Preset Populer**:
  Anda dapat memilih preset siap pakai dari dropdown: *Gaussian Blur, Box Blur, Sharpen, Highpass, Sobel Horisontal/Vertikal, Laplacian, Emboss, dan Identitas*.
* **Divisor & Offset**: Pembagi dapat diatur `auto` (menjumlahkan seluruh bobot) atau angka khusus. Offset digunakan untuk menaikkan level intensitas (misal $+128$).

### 3.7 Fourier Transform (FFT 2D)
* Menghitung **Transformasi Fourier Cepat 2 Dimensi (2D-FFT)** pada citra.
* Menghasilkan visualisasi spektrum magnitudo frekuensi dalam skala logaritmik $\log(1 + |F(u, v)|)$ dengan frekuensi rendah di pusat (*shifted center*).

### 3.8 Colouring (Ruang Warna)
* Mengonversi representasi ruang warna citra:
  * **Binary**: Binarisasi 1-bit.
  * **Grayscale**: Standar luminansi keabuan ITU-R 601.
  * **RGB Adjust**: Menambah atau mengurangi intensitas warna merah, hijau, atau biru.
  * **HSV**: Ruang warna *Hue, Saturation, Value*.
  * **CMY**: Model warna subtraktif *Cyan, Magenta, Yellow*.
  * **YUV**: Model luminansi dan krominansi TV analog PAL.
  * **YIQ**: Model standar televisi NTSC.
  * **Pseudo (Pseudocolor)**: Dialog pemilihan peta warna (*colormap*) untuk visualisasi citra semu ilmiah (pilihan: `jet`, `viridis`, `plasma`, `inferno`, `hot`, `cool`, `rainbow`, dll.).

---

## 4. Panduan Menu: Enhancement (Perbaikan Kualitas Citra)

Menu **Enhancement** digunakan untuk meningkatkan keterbacaan visual dan kontras citra:

### 4.1 Brightness & Contrast
* **Brightness**: Menggeser intensitas kecerahan citra dari $-100$ (lebih gelap) hingga $+100$ (lebih terang).
* **Contrast**: Meregangkan atau mempersempit rentang sebaran histogram citra dari $-100$ s.d $+100$.

### 4.2 Hist. Equalization (Pemerataan Histogram)
* Menerapkan teknik *Cumulative Distribution Function* (CDF) pada kanal intensitas Value (V) untuk meratakan distribusi kontras secara global tanpa merusak rona warna alami (*Hue*).

### 4.3 Smoothing (Penghalusan Citra)
* **Spatial Domain**:
  * **Lowpass Filtering**: Menghaluskan noise halus menggunakan Gaussian blur spasial.
  * **Median Filtering**: Mengganti setiap piksel dengan nilai median jendela tetangga ($3\times3, 5\times5, \dots$). Sangat ampuh menghilangkan derau impuls tanpa mengaburkan garis tepi.
* **Frequency Domain**:
  * **ILPF (Ideal Lowpass Filter)**: Memotong frekuensi tinggi secara tegas pada radius $D_0$.
  * **BLPF (Butterworth Lowpass Filter)**: Transisi pemotongan halus orde $n$ untuk mencegah efek *ringing* (lingkaran riak).

### 4.4 Sharpening (Penajaman Citra)
* **Spatial Domain**:
  * **Highpass Filtering**: Mempertahankan komponen frekuensi spasial tinggi (tepi dan detail tajam).
  * **Highboost Filtering**: Menggabungkan citra asli dengan citra highpass melalui faktor penguat $A \ge 1.0$:
    $$\text{Highboost} = A \cdot I_{\text{asli}} - I_{\text{lowpass}}$$
* **Frequency Domain**:
  * **IHPF (Ideal Highpass Filter)**: Menekan frekuensi rendah di bawah radius cutoff $D_0$.
  * **BHPF (Butterworth Highpass Filter)**: Penapis lolos tinggi Butterworth dengan parameter cutoff $D_0$ dan orde filter $n$.

### 4.5 Geometrics Correction
* Memperbaiki cacat optik kamera atau distorsi sudut pandang:
  * **Shear X & Shear Y**: Memperbaiki kemiringan perspektif.
  * **Distorsi Lensa Radial**: Memperbaiki distorsi cembung (*barrel*) atau cekung (*pincushion*).

---

## 5. Panduan Menu: Noise (Simulasi Gangguan Citra)

Menu **Noise** memungkinkan Anda menguji ketahanan algoritma filter terhadap berbagai distribusi derau sintetis:

1. **Gaussian Noise**: Menambahkan derau acak berdistribusi lonceng Gauss. Parameter: deviasi standar $\sigma$ ($1 \dots 100$).
2. **Rayleigh Noise**: Menambahkan derau asimetris berdistribusi Rayleigh. Parameter: skala $b$.
3. **Erlang (Gamma) Noise**: Menambahkan derau berdistribusi Gamma. Parameter: bentuk $a$ dan skala $b$.
4. **Exponential Noise**: Menambahkan derau berdistribusi eksponensial. Parameter: parameter laju $a$.
5. **Uniform Noise**: Menambahkan derau acak terdistribusi merata dalam interval $[-a, +a]$.
6. **Impulse Noise (Salt & Pepper)**: Menghasilkan bintik-bintik putih murni (255) dan hitam murni (0) secara acak dengan persentase kepadatan $1\% \dots 50\%$.

---

## 6. Panduan Menu: Edge Detection (Deteksi Tepi)

Menu **Edge Detection** digunakan untuk menemukan garis batas objek berdasarkan diskontinuitas intensitas:

### 6.1 1'st Differential Gradient (Gradien Ordo 1)
* **Sobel**: Menghitung magnitudo gradien $\sqrt{G_x^2 + G_y^2}$ dengan pembobotan pusat yang tahan noise.
* **Prewitt**: Menghitung gradien tepi menggunakan kernel rata-rata sederhana horizontal dan vertikal.
* **Robert (Roberts Cross)**: Operator gradien diagonal diferensial $2\times2$ yang sangat cepat.

### 6.2 2'nd Differential Gradient (Gradien Ordo 2)
* **Laplacian**: Operator turunan kedua non-direksional yang sensitif terhadap titik belok intensitas.
* **Laplacian of Gaussian (LoG)**: Menggabungkan penghalusan Gaussian ($\sigma$) sebelum menerapkan Laplacian untuk mencegah penguatan noise acak (*Marr-Hildreth detector*).
* **Canny Edge Detection**: Algoritma deteksi tepi optimal dengan 4 tahapan lengkap:
  1. *Gaussian Smoothing*
  2. *Gradient Magnitude & Angle Calculation*
  3. *Non-Maximum Suppression (NMS)* untuk penipisan garis tepi
  4. *Double Thresholding & Hysteresis Tracking* (Low & High threshold slider)

### 6.3 Compass Edge Detection (Operator Kirsch 8 Arah)
* Mengaplikasikan 8 mask arah mata angin: Utara (N), Barat Laut (NW), Barat (W), Barat Daya (SW), Selatan (S), Tenggara (SE), Timur (E), Timur Laut (NE).
* Mengambil respon nilai maksimum dari kedelapan orientasi untuk menghasilkan kontur tepi yang lengkap di segala arah.

---

## 7. Panduan Menu: Segmentation (Segmentasi Citra)

Menu **Segmentation** memisahkan objek latar depan (*foreground*) dari latar belakang (*background*):

1. **Global Thresholding**: Pemisahan berdasarkan satu nilai ambang intensitas tetap.
2. **Otsu Thresholding**: Menghitung histogram secara otomatis dan memilih ambang batas optimum yang memaksimalkan variansi antarkelas secara matematis.
3. **Adaptive Thresholding**: Menghitung ambang batas lokal berdasarkan nilai rata-rata lingkungan blok tetangga (*Block Size*). Sangat efektif untuk citra dengan pencahayaan tidak merata (bayangan).
4. **K-Means Clustering**: Mengelompokkan piksel warna citra ke dalam $K$ kelompok warna dominan ($K = 2 \dots 8$) menggunakan algoritma iteratif jarak Euclidean.
5. **Region Growing**: Menumbuhkan wilayah segmentasi mulai dari piksel benih (*seed*) di tengah citra berdasarkan kesamaan nilai intensitas piksel tetangga.
6. **Watershed**: Memisahkan batas-batas objek yang saling bersentuhan menggunakan pendekatan topografi peta gradien morfologis.

---

## 8. Panduan Analisis Histogram

Histogram adalah grafik frekuensi yang menunjukkan sebaran intensitas piksel pada citra.

### Menampilkan Jendela Histogram
1. Klik tombol **Histogram RGB** atau **Histogram Grayscale** pada menu bar atau sidebar.
2. Jendela histogram baru akan terbuka (didukung oleh Matplotlib).
3. **Fitur Jendela Histogram**:
   * **Pilihan Sumber Citra**: Pilih radio button **"Hasil"** atau **"Asli"** untuk membandingkan sebaran histogram sebelum dan sesudah pengolahan citra.
   * **Statistik Numerik**: Menampilkan nilai rata-rata ($\mu$), standar deviasi ($\sigma$), median, dan rentang nilai minimum-maksimum.
   * **Tombol Segarkan**: Memperbarui grafik jika Anda baru saja menerapkan filter baru di jendela utama.
   * **Tombol Simpan PNG…**: Mengekspor grafik histogram beresolusi tinggi ke file `.png` untuk lampiran laporan praktikum.

---

## 9. Studi Kasus Alur Kerja Praktikum PCD

### Kasus A: Restorasi Gambar Berderau Bintik (Impulse Noise)
1. Buka gambar dengan menekan **<kbd>Ctrl</kbd> + <kbd>O</kbd>**.
2. Simulasikan kerusakan citra: Pilih menu `Noise → Impulse Noise`, atur kepadatan noise ke $10\%$, lalu klik **Terapkan**.
3. Lakukan restorasi: Pilih menu `Enhancement → Smoothing --> Spatial Domain --> Median Filtering`, pilih ukuran jendela `3×3` atau `5×5`, lalu klik **Terapkan**.
4. **Hasil**: Seluruh bintik garam dan lada akan hilang bersih sementara garis tepi objek tetap terjaga tajam.

### Kasus B: Deteksi Batas Kontur Objek Presisi (Canny Edge)
1. Buka citra objek.
2. Ubah ke tingkat keabuan: Pilih menu `Basic Ops → Colouring --> Grayscale`.
3. Pilih menu `Edge Detection → 2’nd Differential Gradient --> Canny`.
4. Atur ambang: *Low Threshold* = 50, *High Threshold* = 150. Amati *live preview* pada panel kanan.
5. Klik **Terapkan**. Anda akan mendapatkan garis kontur tertutup yang sangat tipis dan bersih.

### Kasus C: Segmentasi Otomatis Objek dengan Otsu
1. Buka gambar (misalnya foto koin atau sel mikroskop).
2. Pilih menu `Segmentation → Otsu Thresholding`.
3. Aplikasi akan langsung menghitung histogram, menemukan ambang pemisah optimal, dan mengisolasi objek dari latarnya secara biner sempurna tanpa perlu menebak angka ambang manual.

---

## 10. Tips & Pemecahan Masalah (Troubleshooting)

* **Gambar Asli Tetap Aman**:
  Semua operasi bersifat *non-destructive*. Citra asli di panel kiri tidak akan pernah berubah atau tertimpa kecuali Anda sengaja memilih *Save* ke file yang sama.
* **Membatalkan Kesalahan**:
  Gunakan tombol **Undo (<kbd>Ctrl</kbd> + <kbd>Z</kbd>)** atau tombol **Reset Asli** jika hasil eksperimen tidak sesuai yang diharapkan.
* **Slider Terasa Lambat pada Gambar Sangat Besar**:
  Aplikasi dilengkapi mekanisme *debounce* otomatis agar slider tetap responsif. Jika gambar beresolusi sangat tinggi (di atas 4K), Anda dapat menggunakan fitur `Geometrics → Zooming` untuk mengecilkan ukuran sementara selama proses eksplorasi.
* **Melihat Informasi Tim Visionary**:
  Pilih menu `About → Info Tim developer` untuk melihat identitas pengembang aplikasi:
  * **Azwa Zahira** (`2407126204`)
  * **Bulan Hijarati Asy-Syiddah** (`2407134878`)
  * **Nur Diana Tri Zahara** (`2407111549`)
  Tersedia tombol satu-klik untuk langsung membuka repositori GitHub dan tutorial YouTube.
