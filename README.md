# Template LaTeX Pra-Skripsi Fasilkom UPN "Veteran" Jawa Timur

Template LaTeX **tidak resmi** untuk pra-skripsi (seminar proposal) Program
Studi Informatika, Fakultas Ilmu Komputer UPN "Veteran" Jawa Timur. Format
disusun dari *Pedoman Penyusunan Laporan Skripsi, Tesis dan Rangkaian
Pelaksanaan Ujian Komprehensif 2025* (SK Dekan No. 0002/UN63.7/SK/TU/2025) dan
template Word skripsi 2025.

> Template ini tidak diterbitkan atau disahkan oleh fakultas. Arahan dosen
> pembimbing, koordinator/PIC skripsi program studi, dan pedoman terbaru selalu
> diutamakan.

## Format yang diterapkan

| Aturan | Nilai |
|---|---|
| Kertas | A4, satu sisi |
| Margin | kiri 4 cm; atas, kanan, bawah 3 cm |
| Huruf isi | Times New Roman 12 pt |
| Spasi | 1,5 baris; daftar pustaka 1 spasi |
| Judul bab | `BAB I` lalu judul pada baris berikutnya, 14 pt tebal, rata tengah |
| Subbab | `1.1.` dan `1.1.1.`, 12 pt tebal |
| Tabel | judul di atas, rata kiri, tebal; `Sumber:` di bawah |
| Gambar | judul di bawah, rata tengah, tebal |
| Persamaan | nomor `(2.1)` di batas kanan |
| Kode sumber | Courier New 9 pt, spasi tunggal, bernomor baris |
| Nomor halaman | romawi kecil untuk bagian awal, arab mulai BAB I, tengah bawah |
| Daftar pustaka | gaya IEEE |
| Sampul | Arial, logo 4 × 4 cm, pita oranye `#ff914d` dan kuning `#f4ff00` |

## Instalasi

Yang dibutuhkan:

| Kebutuhan | Untuk apa |
|---|---|
| TeX Live 2024+ / MacTeX (XeLaTeX, Biber, `latexmk`) | wajib, untuk build PDF |
| Font Times New Roman, Arial, Courier New | hasil akhir sesuai pedoman (sudah ada di macOS dan Windows) |
| `make` | opsional, pintasan perintah |
| Python 3 dan Poppler (`pdftotext`, `pdffonts`) | opsional, hanya untuk `make check` |

Tidak ingin memasang apa pun? Pakai [Overleaf](#overleaf).

### macOS (sudah diuji)

Diuji pada macOS Apple Silicon dengan MacTeX 2026 lewat Homebrew.

1. Pasang MacTeX. Unduhannya sekitar **7 GB** dan memakan sekitar **10 GB**
   ruang disk.

   ```sh
   brew install --cask mactex-no-gui
   ```

   Jika unduhan terputus di tengah jalan (`curl: (56)` atau `curl: (92)`),
   jalankan ulang perintahnya atau unduh `MacTeX.pkg` langsung dari
   <https://tug.org/mactex/>.

2. Buka **terminal baru**, lalu periksa:

   ```sh
   xelatex --version && biber --version && latexmk --version
   ```

   Jika muncul `command not found` padahal MacTeX sudah terpasang, tautan
   `/Library/TeX/texbin` belum dibuat. Buat manual, lalu buka terminal baru:

   ```sh
   sudo mkdir -p /Library/TeX
   sudo ln -s /usr/local/texlive/2026/bin/universal-darwin /Library/TeX/texbin
   ```

   Sesuaikan `2026` dengan versi yang terpasang (`ls /usr/local/texlive`).

3. Opsional, untuk `make` dan `make check`:

   ```sh
   xcode-select --install   # menyediakan make
   brew install poppler     # menyediakan pdftotext dan pdffonts
   ```

**Ruang disk terbatas?** BasicTeX jauh lebih kecil (sekitar 100 MB), tetapi
paketnya harus dipasang sendiri. Langkah ini belum diuji penuh:

```sh
brew install --cask basictex
# buka terminal baru
sudo tlmgr update --self
sudo tlmgr install latexmk biber biblatex biblatex-ieee babel-indonesian \
  csquotes setspace titlesec caption booktabs enumitem xurl kvoptions \
  xkeyval listings tex-gyre tex-gyre-math pgf multirow unicode-math tools
```

Jika build gagal dengan pesan ``File `xyz.sty' not found``, pasang paket yang
kurang dengan `sudo tlmgr install xyz`.

**Biber gagal setelah pembaruan macOS.** Jika muncul pesan seperti

```text
biber: extracting arm64 binary with lipo failed (wstatus=256)
```

daftar pustaka menjadi kosong dan `latexmk` berhenti dengan galat. Biber bawaan
TeX Live adalah *universal binary* yang membongkar dirinya saat dijalankan, dan
proses itu dapat rusak setelah macOS diperbarui. Perbaiki dengan mengambil
bagian arm64-nya satu kali:

```sh
lipo -thin arm64 -output /tmp/biber /Library/TeX/texbin/biber
sudo cp /tmp/biber /usr/local/bin/biber
biber --version    # harus cocok dengan versi bawaan TeX Live
```

Jangan memasang Biber dari Homebrew kecuali versinya sama dengan bawaan TeX
Live; versi yang berbeda akan menolak berkas `.bcf` yang dihasilkan biblatex.

### Windows (belum diuji)

> **Perhatian:** langkah Windows di bawah ini disusun dari dokumentasi TeX Live
> dan **belum pernah dicoba** oleh pembuat template. Jika Anda berhasil (atau
> gagal), silakan buka *issue* agar panduan ini bisa diperbaiki.

1. Unduh dan jalankan `install-tl-windows.exe` dari
   <https://tug.org/texlive/windows.html>. Pilih skema lengkap (*full scheme*)
   agar XeLaTeX, Biber, `latexmk`, dan semua paket langsung tersedia. TeX Live
   untuk Windows sudah membawa Perl yang dibutuhkan `latexmk`.
2. Buka **Command Prompt/PowerShell baru**, lalu periksa:

   ```bat
   xelatex --version
   biber --version
   latexmk --version
   ```

3. Windows biasanya tidak memiliki `make`. Build langsung dengan:

   ```bat
   latexmk -outdir=build praskripsi.tex
   ```

4. Opsional, untuk pemeriksaan PDF: pasang Python 3 dan Poppler untuk Windows,
   pastikan keduanya ada di `PATH`, lalu jalankan:

   ```bat
   python scripts\check_pdf.py build\praskripsi.pdf --log build\praskripsi.log
   ```

MiKTeX juga dapat dipakai, tetapi `latexmk` pada MiKTeX memerlukan Perl yang
dipasang terpisah (misalnya Strawberry Perl). Karena itu TeX Live lebih
disarankan.

## Mulai cepat

1. Isi identitas pada `metadata.tex`.
2. Tulis isi di `chapters/` dan referensi di `bibliography/references.bib`.
3. Jalankan `make`, lalu buka `build/praskripsi.pdf`.

```sh
make          # build PDF ke build/praskripsi.pdf
make watch    # build ulang otomatis setiap berkas disimpan
make check    # build + periksa ukuran kertas, font, margin, dan rujukan
make clean    # hapus build/
```

Tanpa `make`: `latexmk -outdir=build praskripsi.tex`.

## Struktur

```text
metadata.tex                      judul, nama, NPM, dosen pembimbing
praskripsi.tex                    berkas utama (urutan bagian dokumen)
upnjatim-skripsi.cls              seluruh aturan format
chapters/bab1-pendahuluan.tex
chapters/bab2-tinjauan-pustaka.tex
chapters/bab3-metodologi.tex
bibliography/references.bib
frontmatter/daftar-notasi.tex     opsional, aktifkan di praskripsi.tex
appendices/lampiran-1.tex
```

## Perintah yang tersedia

| Perintah | Fungsi |
|---|---|
| `\buatsampul` | sampul pra-skripsi |
| `\daftarisi`, `\daftargambar`, `\daftartabel` | daftar pada bagian awal |
| `\bagianutama` | mulai penomoran arab |
| `\daftarpustaka` | cetak daftar pustaka IEEE |
| `\lampiran{Judul}` | mulai lampiran bernomor |
| `\sumber{...}` | baris sumber di bawah tabel/gambar |

Opsi class:

```latex
\documentclass[jenis=praskripsi]{upnjatim-skripsi}   % bawaan
\documentclass[sampul=oranye]{upnjatim-skripsi}      % sampul latar oranye (softcover)
\documentclass[ketat]{upnjatim-skripsi}              % gagal jika font resmi tidak ada
\documentclass[pemenggalan]{upnjatim-skripsi}        % izinkan kata dipenggal dengan tanda hubung
```

Secara bawaan kata **tidak dipenggal** di ujung baris, mengikuti pedoman dan
template Word: kata yang tidak muat dipindahkan utuh ke baris berikutnya.
Akibatnya jarak antarkata pada teks rata kanan-kiri bisa melebar, persis
seperti keluaran Word. Opsi `pemenggalan` mengembalikan perilaku LaTeX biasa
yang memakai tanda hubung.

Tanpa opsi `ketat`, font TeX Gyre (Termes, Heros, Cursor) otomatis dipakai bila
font resmi tidak tersedia, misalnya di Overleaf. Gunakan font resmi untuk
berkas yang dikumpulkan.

## Ekspor ke Microsoft Word

Dosen pembimbing sering meminta berkas Word untuk konsultasi. Jangan mengubah
PDF menjadi Word karena tata letaknya rusak. Pakai:

```sh
make docx      # menghasilkan build/praskripsi.docx
```

Prasyarat: **Pandoc**. macOS: `brew install pandoc`. Windows: unduh pemasang
dari <https://pandoc.org/installing.html>.

Berkas `.docx` dibuat langsung dari sumber LaTeX, sehingga:

- gaya Word disetel sesuai pedoman: Times New Roman 12 pt, spasi 1,5, margin
  4/3/3/3 cm, judul bab 14 pt tebal rata tengah;
- judul bernomor seperti pedoman (`BAB I PENDAHULUAN`, `1.1.`, `1.1.1.`);
- rumus menjadi persamaan Word asli yang masih dapat disunting;
- sitasi `\cite{...}` menjadi `[1]` dan daftar pustaka IEEE ikut tercetak,
  dibuat dari `bibliography/references.bib` memakai `assets/ieee.csl`;
- acuan `\ref{...}` diganti nomornya, misalnya `Persamaan 2.1`.

Bagian yang sama seperti PDF:

- **sampul** disisipkan sebagai gambar halaman penuh, diambil dari halaman
  pertama PDF (karena itu PDF dibuat lebih dulu bila belum ada);
- **daftar isi, daftar gambar, dan daftar tabel** berupa *field* Word yang
  memuat nomor halaman sebenarnya. Word memperbaruinya saat berkas dibuka; bila
  masih kosong, klik kanan daftarnya lalu pilih **Update Field**;
- **nomor halaman** di tengah bawah: angka romawi untuk bagian awal dan angka
  arab mulai dari BAB I.

Yang masih berbeda:

- penomoran halaman Word tidak persis sama dengan PDF karena Word mengatur
  ulang baris dan pemenggalan halaman;
- gambar TikZ diganti penanda teks; gambar dari berkas biasa tetap ikut;
- judul tabel diletakkan Word di bawah tabel, bukan di atas;
- sampul berupa gambar, jadi teksnya tidak dapat disunting di Word. Ubah
  `metadata.tex` lalu jalankan `make docx` lagi.

Perbaikan dari dosen tetap diterapkan pada berkas `.tex`, lalu `make docx`
dijalankan ulang. PDF resmi tetap dihasilkan `make`.

**Jika dosen memakai Mendeley:** sitasi pada `.docx` berupa teks biasa, bukan
kolom (*field*) Mendeley, sehingga dosen tidak dapat memutakhirkannya langsung
dari Mendeley. Catat referensi baru dari dosen ke `bibliography/references.bib`.
Untuk mengelola pustaka sendiri, Zotero dengan pengaya Better BibTeX dapat
mengekspor `.bib` secara otomatis.

## Overleaf

Unggah seluruh isi repositori, pilih compiler **XeLaTeX**, dan jadikan
`praskripsi.tex` sebagai berkas utama.

## Belum dikonfirmasi

- Halaman awal yang wajib untuk pra-skripsi (misalnya lembar persetujuan
  seminar proposal) tidak dirinci dalam pedoman. Tanyakan koordinator/PIC
  skripsi program studi.
- Contoh daftar pustaka pada pedoman halaman 23 memakai IEEE, tetapi lampiran
  pedoman halaman 41–43 memakai contoh author-year. Template ini memakai IEEE.
- Mode `jenis=skripsi` baru menyediakan sampul; halaman pengesahan,
  persetujuan, orisinalitas, dan abstrak belum tersedia.

## Lisensi

Kode dan dokumentasi dirilis dengan **LPPL 1.3c atau lebih baru**. Struktur
class diadaptasi dari template tidak resmi proposal skripsi FILKOM UB karya
Pande Kadek Nathan Prabhaswara Sudiara Putra (LPPL 1.3c). Logo UPN "Veteran"
Jawa Timur tidak tercakup LPPL; lihat `assets/NOTICE.md`.

`assets/ieee.csl` berasal dari proyek
[Citation Style Language](https://github.com/citation-style-language/styles)
dan berlisensi CC BY-SA 3.0, terpisah dari LPPL.
