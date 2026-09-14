#!/usr/bin/env python3
"""Periksa PDF hasil build terhadap aturan utama Pedoman Skripsi Fasilkom UPN Jatim 2025."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PT_PER_MM = 72 / 25.4
A4_PT = (595.28, 841.89)
MARGIN_MM = {"left": 40.0, "right": 30.0}
TOLERANCE_MM = 0.6
REQUIRED_TEXT = [
    "PRA-SKRIPSI",
    "DOSEN PEMBIMBING",
    "DAFTAR ISI",
    "BAB I",
    "PENDAHULUAN",
    "DAFTAR PUSTAKA",
]
REQUIRED_FONTS = {
    "Times New Roman": "TimesNewRomanPSMT",
    "Times New Roman Bold": "TimesNewRomanPS-BoldMT",
    "Arial": "ArialMT",
}
LOG_PATTERNS = [
    r"LaTeX Warning: (Reference|Citation) .* undefined",
    r"There were undefined references",
    r"Please \(re\)run Biber",
    r"Missing character: There is no",
    r"Overfull \\hbox \((\d{2,}|[3-9])\.\d+pt too wide\)",
]


def run(*command: str) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{command[0]} gagal: {result.stderr.strip()}")
    return result.stdout


def check_page_size(pdf: Path) -> list[str]:
    match = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", run("pdfinfo", str(pdf)))
    if not match:
        return ["Ukuran halaman tidak terbaca"]
    width, height = float(match.group(1)), float(match.group(2))
    if abs(width - A4_PT[0]) > 1 or abs(height - A4_PT[1]) > 1:
        return [f"Halaman bukan A4: {width:.1f} x {height:.1f} pt"]
    return []


def check_fonts(pdf: Path) -> list[str]:
    output = run("pdffonts", str(pdf))
    errors = [f"Font {label} tidak tertanam" for label, ps in REQUIRED_FONTS.items() if ps not in output]
    # TeX Gyre Termes Math sengaja dipakai untuk rumus; hanya font teks pengganti yang dilaporkan.
    if re.search(r"TeXGyre(?!\w*Math)", output):
        errors.append("Font pengganti TeX Gyre dipakai; pasang Times New Roman/Arial/Courier New untuk hasil akhir")
    return errors


def check_text(pdf: Path) -> list[str]:
    text = run("pdftotext", "-layout", str(pdf), "-")
    errors = [f"Teks wajib tidak ditemukan: {needle}" for needle in REQUIRED_TEXT if needle not in text]
    if "??" in text:
        errors.append("Ada rujukan tak terdefinisi (??) di PDF")
    return errors


def check_margins(pdf: Path) -> list[str]:
    """Teks isi (selain sampul) harus berada di dalam margin kiri 4 cm dan kanan 3 cm."""
    html = run("pdftotext", "-f", "2", "-bbox", str(pdf), "-")
    errors = []
    for number, page in enumerate(re.findall(r'<page width="([\d.]+)"[^>]*>(.*?)</page>', html, re.S), 2):
        width = float(page[0])
        for x_min, x_max, word in re.findall(r'<word xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)"[^>]*>([^<]*)</word>', page[1]):
            left = float(x_min) / PT_PER_MM
            right = (width - float(x_max)) / PT_PER_MM
            if left < MARGIN_MM["left"] - TOLERANCE_MM or right < MARGIN_MM["right"] - TOLERANCE_MM:
                errors.append(f"Halaman PDF {number}: '{word}' keluar margin (kiri {left:.1f} mm, kanan {right:.1f} mm)")
                break
    return errors


def check_log(log: Path) -> list[str]:
    text = log.read_text(encoding="utf-8", errors="replace")
    return [f"Log: pola '{pattern}' ditemukan" for pattern in LOG_PATTERNS if re.search(pattern, text)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args()
    if not args.pdf.is_file():
        print(f"PDF tidak ditemukan: {args.pdf}", file=sys.stderr)
        return 2

    errors = check_page_size(args.pdf) + check_fonts(args.pdf) + check_text(args.pdf) + check_margins(args.pdf)
    if args.log and args.log.is_file():
        errors += check_log(args.log)

    for error in errors:
        print(f"GAGAL  {error}")
    if errors:
        return 1
    print(f"LULUS  {args.pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
