#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ROMAWI = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

# Ukuran dalam satuan Word: sz = setengah poin, spacing = twip (1/20 poin).
TNR = "Times New Roman"
SZ_ISI = "24"      # 12 pt
SZ_BAB = "28"      # 14 pt
SZ_KODE = "18"     # 9 pt
SPASI_15 = "360"   # 1,5 baris
IND_BARIS = "720"   # indentasi baris pertama 1,27 cm
LEBAR_TEKS = "7938" # 14 cm: lebar teks A4 dengan margin 4 cm dan 3 cm
GAYA_TANPA_NOMOR = "JudulTanpaNomor"
MARGIN = {"left": "2268", "right": "1701", "top": "1701", "bottom": "1701"}


def mati(pesan: str) -> None:
    print(f"GAGAL  {pesan}", file=sys.stderr)
    raise SystemExit(1)


def baca(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def urutan_input(utama: Path) -> list[Path]:
    """Ambil urutan \\input{...} dari berkas utama, lewati baris berkomentar."""
    berkas = []
    for baris in baca(utama).splitlines():
        if baris.lstrip().startswith("%"):
            continue
        for nama in re.findall(r"\\input\{([^}]+)\}", baris):
            if nama == "metadata":
                continue
            kandidat = ROOT / (nama if nama.endswith(".tex") else f"{nama}.tex")
            if kandidat.is_file():
                berkas.append(kandidat)
    return berkas


def metadata() -> dict[str, str]:
    teks = baca(ROOT / "metadata.tex")
    return {k: v.strip() for k, v in re.findall(r"([a-z-]+)=\{(.*?)\},?\s*\n", teks, re.S)}


def blok_judul(meta: dict[str, str]) -> str:
    baris = [
        "PRA-SKRIPSI",
        f"\\textbf{{{meta.get('judul', '')}}}",
        f"{meta.get('nama', '')}",
        f"NPM {meta.get('npm', '')}",
        "Dosen Pembimbing:",
    ]
    for kunci in ("pembimbing-satu", "pembimbing-dua"):
        if meta.get(kunci):
            baris.append(meta[kunci])
    baris.append(f"Program Studi {meta.get('program-studi', 'Informatika')}")
    baris.append("Fakultas Ilmu Komputer")
    baris.append("UPN \"Veteran\" Jawa Timur")
    baris.append(meta.get("tahun", ""))
    return "\n\n".join(baris) + "\n\n"


def ganti_perintah(teks: str, nama: str, ubah) -> str:
    """Ganti \\nama{...} dengan menghitung kurung, agar argumen bersarang aman."""
    hasil = []
    sisa = teks
    while True:
        awal = sisa.find(f"\\{nama}{{")
        if awal < 0:
            hasil.append(sisa)
            return "".join(hasil)
        mulai = awal + len(nama) + 2
        dalam = 1
        posisi = mulai
        while posisi < len(sisa) and dalam:
            if sisa[posisi] == "{":
                dalam += 1
            elif sisa[posisi] == "}":
                dalam -= 1
            posisi += 1
        hasil.append(sisa[:awal])
        hasil.append(ubah(sisa[mulai : posisi - 1]))
        sisa = sisa[posisi:]


def bersihkan(teks: str, nomor_bab: int) -> str:
    """Terjemahkan perintah khusus class agar dimengerti Pandoc."""
    # TikZ tidak dapat dirender Pandoc; beri penanda agar tidak hilang diam-diam.
    teks = re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        r"\\textit{[Gambar TikZ hanya tersedia pada versi PDF]}",
        teks,
        flags=re.S,
    )
    teks = ganti_perintah(teks, "sumber", lambda isi: f"\n\nSumber: {isi}\n\n")
    teks = ganti_perintah(teks, "lampiran", lambda isi: f"\\chapter{{Lampiran: {isi}}}")
    teks = teks.replace("\\checkmark", "✓")

    # Nomor subbab tidak ditulis sebagai teks; Word menomorinya sendiri lewat
    # daftar bertingkat yang ditautkan ke gaya Heading (lihat _pasang_penomoran).
    return teks


def kumpulkan_label(berkas: list[Path]) -> dict[str, str]:
    """Petakan label ke nomor (mis. eq:bobot -> 2.1) seperti penomoran LaTeX."""
    peta: dict[str, str] = {}
    bab = 0
    for path in berkas:
        teks = baca(path)
        if "\\chapter{" in teks and "\\lampiran{" not in teks:
            bab += 1
        cacah = {"equation": 0, "table": 0, "figure": 0}
        for m in re.finditer(r"\\begin\{(equation|table|figure)\}(.*?)\\end\{\1\}", teks, re.S):
            jenis, isi = m.group(1), m.group(2)
            cacah[jenis] += 1
            label = re.search(r"\\label\{([^}]+)\}", isi)
            if label:
                peta[label.group(1)] = f"{bab}.{cacah[jenis]}"
    return peta


def sumber_gabungan(meta: dict[str, str], berkas: list[Path], blok_sampul: bool = True) -> str:
    # Blok judul teks hanya dipakai bila gambar sampul tidak tersedia, agar
    # sampulnya tidak tampil dua kali.
    bagian = [blok_judul(meta)] if blok_sampul else []
    peta_label = kumpulkan_label(berkas)
    nomor_bab = 0
    pustaka_tercetak = False
    for path in berkas:
        teks = baca(path)
        teks = re.sub(r"\\ref\{([^}]+)\}", lambda m: peta_label.get(m.group(1), "?"), teks)
        # Daftar pustaka dicetak sebelum lampiran, sama seperti keluaran PDF.
        if "\\lampiran{" in teks and not pustaka_tercetak:
            bagian.append("\\chapter{DAFTAR PUSTAKA}\n")
            pustaka_tercetak = True
        judul = re.search(r"\\chapter\{([^}]*)\}", teks)
        if judul and "\\lampiran" not in teks:
            nomor_bab += 1
            judul_bab = f"BAB {ROMAWI[nomor_bab]} {judul.group(1).upper()}"
            teks = teks.replace(judul.group(0), f"\\chapter{{{judul_bab}}}", 1)
        bagian.append(bersihkan(teks, nomor_bab))
    if not pustaka_tercetak:
        bagian.append("\\chapter{DAFTAR PUSTAKA}\n")
    return "\n\n".join(bagian)


def _anak(induk: ET.Element, tag: str) -> ET.Element:
    ada = induk.find(f"{W}{tag}")
    if ada is None:
        ada = ET.SubElement(induk, f"{W}{tag}")
    return ada


def _atur(induk: ET.Element, tag: str, **atribut: str) -> None:
    simpul = _anak(induk, tag)
    for kunci, nilai in atribut.items():
        simpul.set(f"{W}{kunci}", nilai)


def _gaya(akar: ET.Element, style_id: str) -> ET.Element | None:
    for gaya in akar.findall(f"{W}style"):
        if gaya.get(f"{W}styleId") == style_id:
            return gaya
    return None


def _atur_font(gaya: ET.Element, ukuran: str, tebal: bool, miring: bool = False) -> None:
    rpr = _anak(gaya, "rPr")
    _atur(rpr, "rFonts", ascii=TNR, hAnsi=TNR, cs=TNR)
    _atur(rpr, "sz", val=ukuran)
    _atur(rpr, "szCs", val=ukuran)
    _atur(rpr, "color", val="auto")
    for tag, aktif in (("b", tebal), ("i", miring)):
        simpul = _anak(rpr, tag)
        simpul.set(f"{W}val", "1" if aktif else "0")


def reference_docx(tujuan: Path) -> Path:
    """Buat reference.docx dari bawaan Pandoc, lalu setel gayanya sesuai pedoman."""
    bawaan = tujuan.parent / "reference-bawaan.docx"
    with bawaan.open("wb") as keluar:
        subprocess.run(
            ["pandoc", "--print-default-data-file", "reference.docx"],
            stdout=keluar, check=True,
        )

    with zipfile.ZipFile(bawaan) as zin:
        isi = {nama: zin.read(nama) for nama in zin.namelist()}

    for awalan in (f"{W}", ""):
        ET.register_namespace("w" if awalan else "", W.strip("{}"))
        break

    akar = ET.fromstring(isi["word/styles.xml"])
    bawaan_gaya = akar.find(f"{W}docDefaults")
    if bawaan_gaya is not None:
        rpr = _anak(_anak(bawaan_gaya, "rPrDefault"), "rPr")
        _atur(rpr, "rFonts", ascii=TNR, hAnsi=TNR, cs=TNR)
        _atur(rpr, "sz", val=SZ_ISI)
        _atur(rpr, "szCs", val=SZ_ISI)
        ppr = _anak(_anak(bawaan_gaya, "pPrDefault"), "pPr")
        _atur(ppr, "spacing", line=SPASI_15, lineRule="auto", before="0", after="0")
        _atur(ppr, "jc", val="both")

    aturan = {
        "Normal": (SZ_ISI, False, "both", None),
        "BodyText": (SZ_ISI, False, "both", None),
        "FirstParagraph": (SZ_ISI, False, "both", None),
        "Compact": (SZ_ISI, False, "both", None),
        "Heading1": (SZ_BAB, True, "center", ("0", "240")),
        "Heading2": (SZ_ISI, True, "left", ("240", "120")),
        "Heading3": (SZ_ISI, True, "left", ("180", "120")),
        "Heading4": (SZ_ISI, True, "left", ("180", "120")),
        "Caption": (SZ_ISI, True, "left", ("120", "120")),
        "TableCaption": (SZ_ISI, True, "left", ("120", "120")),
        "ImageCaption": (SZ_ISI, True, "center", ("120", "120")),
        "Bibliography": (SZ_ISI, False, "both", None),
        "Title": (SZ_BAB, True, "center", ("240", "240")),
        "Author": (SZ_ISI, False, "center", None),
    }
    for style_id, (ukuran, tebal, rata, jarak) in aturan.items():
        gaya = _gaya(akar, style_id)
        if gaya is None:
            continue
        _atur_font(gaya, ukuran, tebal)
        ppr = _anak(gaya, "pPr")
        _atur(ppr, "jc", val=rata)
        if jarak:
            _atur(ppr, "spacing", before=jarak[0], after=jarak[1], line=SPASI_15, lineRule="auto")

    # Paragraf isi: baris pertama masuk 1,27 cm dan jarak antarparagraf 6 pt,
    # sama seperti keluaran PDF. Judul, keterangan, dan pustaka tanpa indentasi.
    for style_id in ("Normal", "BodyText", "FirstParagraph"):
        gaya = _gaya(akar, style_id)
        if gaya is not None:
            ppr = _anak(gaya, "pPr")
            _atur(ppr, "ind", firstLine=IND_BARIS)
            _atur(ppr, "spacing", before="0", after="120", line=SPASI_15, lineRule="auto")
    # "Compact" dipakai Pandoc untuk butir daftar; butir tidak boleh menjorok.
    for style_id in ("Compact", "Heading1", "Heading2", "Heading3", "Heading4", "Caption",
                     "TableCaption", "ImageCaption", "Bibliography", "SourceCode"):
        gaya = _gaya(akar, style_id)
        if gaya is not None:
            _atur(_anak(gaya, "pPr"), "ind", firstLine="0", left="0")

    # Word mengutamakan atribut tema (asciiTheme/themeColor) daripada nilai
    # eksplisit. Tanpa dibuang, huruf ikut tema (Aptos) dan judul berwarna.
    for simpul in akar.iter(f"{W}rFonts"):
        for atribut in ("asciiTheme", "hAnsiTheme", "cstheme", "eastAsiaTheme"):
            simpul.attrib.pop(f"{W}{atribut}", None)
    for gaya in akar.findall(f"{W}style"):
        if "Hyperlink" in (gaya.get(f"{W}styleId") or ""):
            continue
        for simpul in gaya.iter(f"{W}color"):
            for atribut in ("themeColor", "themeShade", "themeTint"):
                simpul.attrib.pop(f"{W}{atribut}", None)
            simpul.set(f"{W}val", "000000")

    # Tiap bab mulai di halaman baru, sama seperti PDF.
    bab = _gaya(akar, "Heading1")
    if bab is not None:
        _anak(_anak(bab, "pPr"), "pageBreakBefore")

    # Tabel Pandoc tidak bergaris; PDF memakai garis penuh, jadi disamakan.
    tabel = _gaya(akar, "Table")
    if tabel is not None:
        tblpr = _anak(tabel, "tblPr")
        garis = _anak(tblpr, "tblBorders")
        for sisi in ("top", "left", "bottom", "right", "insideH", "insideV"):
            _atur(garis, sisi, val="single", sz="4", space="0", color="000000")
        marjin = _anak(tblpr, "tblCellMar")
        for sisi in ("left", "right"):
            _atur(marjin, sisi, w="108", type="dxa")
        ppr = _anak(tabel, "pPr")
        _atur(ppr, "ind", firstLine="0", left="0")
        _atur(ppr, "spacing", before="0", after="0", line="240", lineRule="auto")

    # Gaya judul tanpa nomor untuk bagian awal, daftar pustaka, dan lampiran.
    # Tetap outlineLvl 0 agar ikut tercantum di Daftar Isi, tetapi tidak
    # menambah hitungan bab sehingga subbab BAB I tetap 1.1.
    if _gaya(akar, GAYA_TANPA_NOMOR) is None:
        gaya = ET.SubElement(akar, f"{W}style")
        gaya.set(f"{W}type", "paragraph")
        gaya.set(f"{W}styleId", GAYA_TANPA_NOMOR)
        _atur(gaya, "name", val="Judul Tanpa Nomor")
        _atur(gaya, "basedOn", val="Heading1")
        _atur(gaya, "next", val="BodyText")
        ppr = _anak(gaya, "pPr")
        _atur(ppr, "outlineLvl", val="0")
        _atur(ppr, "ind", left="0", firstLine="0")
    # Gaya ini diturunkan dari Heading1 sehingga ikut mewarisi penomorannya.
    # numId 0 mematikan penomoran, agar judul seperti DAFTAR ISI tidak
    # terhitung sebagai bab dan subbab BAB I tetap mulai dari 1.1.
    numpr = _anak(_anak(_gaya(akar, GAYA_TANPA_NOMOR), "pPr"), "numPr")
    _atur(numpr, "ilvl", val="0")
    _atur(numpr, "numId", val="0")

    # Gaya entri Daftar Isi. Tanpa ini Word menurunkannya dari Normal yang
    # rata kanan-kiri dan menjorok, sehingga entrinya berantakan.
    for tingkat in range(1, 4):
        style_id = f"TOC{tingkat}"
        gaya = _gaya(akar, style_id)
        if gaya is None:
            gaya = ET.SubElement(akar, f"{W}style")
            gaya.set(f"{W}type", "paragraph")
            gaya.set(f"{W}styleId", style_id)
            _atur(gaya, "name", val=f"toc {tingkat}")
            _atur(gaya, "basedOn", val="Normal")
        ppr = _anak(gaya, "pPr")
        _atur(ppr, "jc", val="left")
        _atur(ppr, "spacing", before="0", after="0", line=SPASI_15, lineRule="auto")
        _atur(ppr, "ind", left=str((tingkat - 1) * 360), firstLine="0")
        tabs = _anak(ppr, "tabs")
        for simpul in tabs.findall(f"{W}tab"):
            tabs.remove(simpul)
        _atur(tabs, "tab", val="right", leader="dot", pos=LEBAR_TEKS)

    kode = _gaya(akar, "SourceCode") or _gaya(akar, "VerbatimChar")
    if kode is not None:
        rpr = _anak(kode, "rPr")
        _atur(rpr, "rFonts", ascii="Courier New", hAnsi="Courier New", cs="Courier New")
        _atur(rpr, "sz", val=SZ_KODE)
        _atur(rpr, "szCs", val=SZ_KODE)
    isi["word/styles.xml"] = ET.tostring(akar, encoding="UTF-8", xml_declaration=True)

    dokumen = ET.fromstring(isi["word/document.xml"])
    for sect in dokumen.iter(f"{W}sectPr"):
        _atur(sect, "pgMar", header="709", footer="709", gutter="0", **MARGIN)
    isi["word/document.xml"] = ET.tostring(dokumen, encoding="UTF-8", xml_declaration=True)

    # Tema pun disetel ke Times New Roman, untuk gaya yang masih mewarisinya.
    if "word/theme/theme1.xml" in isi:
        tema = isi["word/theme/theme1.xml"].decode("utf-8")
        tema = re.sub(r'(<a:latin typeface=")[^"]*(")', rf"\g<1>{TNR}\g<2>", tema)
        isi["word/theme/theme1.xml"] = tema.encode("utf-8")

    with zipfile.ZipFile(tujuan, "w", zipfile.ZIP_DEFLATED) as zout:
        for nama, data in isi.items():
            zout.writestr(nama, data)
    bawaan.unlink()
    return tujuan


NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
)
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
ID_SAMPUL = "rIdSampulUPN"
ID_FOOTER = "rIdFooterUPN"
EMU_MM = 36000
A4_EMU = (210 * EMU_MM, 297 * EMU_MM)


def pdf_siap(utama: Path, pdf: Path) -> Path | None:
    """Sampul .docx diambil dari halaman pertama PDF, jadi PDF harus ada."""
    if pdf.is_file():
        return pdf
    if shutil.which("latexmk") is None:
        return None
    # Jalankan seperti Makefile (jalur relatif), agar Biber menemukan berkasnya.
    subprocess.run(
        ["latexmk", f"-outdir={pdf.parent.relative_to(ROOT)}",
         str(utama.relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    return pdf if pdf.is_file() else None


def render_sampul(pdf: Path, tujuan: Path) -> Path | None:
    if shutil.which("pdftoppm") is None:
        return None
    subprocess.run(
        ["pdftoppm", "-f", "1", "-l", "1", "-r", "200", "-png", "-singlefile",
         str(pdf), str(tujuan.with_suffix(""))],
        check=False, capture_output=True,
    )
    return tujuan if tujuan.is_file() else None


def _p_judul(teks: str) -> str:
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="{GAYA_TANPA_NOMOR}"/></w:pPr>'
            f"<w:r><w:t>{teks}</w:t></w:r></w:p>")


def _p_field(instruksi: str) -> str:
    """Field TOC. Atribut w:dirty membuat Word memperbaruinya saat dibuka."""
    return (
        f'<w:p {NS}><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
        f'<w:r><w:instrText xml:space="preserve">{instruksi}</w:instrText></w:r>'
        f'<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        f"<w:r><w:t>Klik kanan daftar ini lalu pilih Update Field.</w:t></w:r>"
        f'<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
    )


def _p_sampul() -> str:
    lebar, tinggi = A4_EMU
    return (
        f'<w:p {NS}><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" '
        f'w:lineRule="auto"/><w:ind w:left="0" w:right="0" w:firstLine="0"/>'
        f'<w:jc w:val="left"/></w:pPr><w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{lebar}" cy="{tinggi}"/><wp:docPr id="991" name="Sampul"/>'
        f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic><pic:nvPicPr><pic:cNvPr id="991" name="Sampul"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{ID_SAMPUL}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{lebar}" cy="{tinggi}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
        f"</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
    )


ID_NOMOR = "900"


def _abstract_num() -> ET.Element:
    """Daftar bertingkat yang ditautkan ke gaya Heading, seperti multilevel list Word.

    Tingkat 1 hanya menghitung bab tanpa mencetak apa pun, karena kata
    "BAB I" sudah menjadi bagian teks judulnya. Tingkat berikutnya memakai
    angka bab tersebut sehingga menghasilkan 1.1., 1.1.1., dan seterusnya.
    """
    pola = {0: "", 1: "%1.%2.", 2: "%1.%2.%3.", 3: "%1.%2.%3.%4."}
    abstrak = ET.Element(f"{W}abstractNum")
    abstrak.set(f"{W}abstractNumId", ID_NOMOR)
    for tingkat, teks in pola.items():
        lvl = ET.SubElement(abstrak, f"{W}lvl")
        lvl.set(f"{W}ilvl", str(tingkat))
        _atur(lvl, "start", val="1")
        _atur(lvl, "numFmt", val="decimal")
        _atur(lvl, "pStyle", val=f"Heading{tingkat + 1}")
        _atur(lvl, "lvlText", val=teks)
        _atur(lvl, "lvlJc", val="left")
        _atur(lvl, "suff", val="none" if tingkat == 0 else "tab")
        ppr = _anak(lvl, "pPr")
        _atur(ppr, "ind", left="0", firstLine="0")
        tabs = _anak(ppr, "tabs")
        _atur(tabs, "tab", val="left", pos=IND_BARIS)
    return abstrak


def _pasang_penomoran(isi: dict[str, bytes]) -> None:
    """Tautkan gaya Heading ke daftar bertingkat agar Word menomori sendiri."""
    if "word/numbering.xml" not in isi:
        return
    mentah = isi["word/numbering.xml"].decode("utf-8")
    for prefiks, uri in re.findall(r'xmlns:([A-Za-z0-9]+)="([^"]+)"', mentah):
        ET.register_namespace(prefiks, uri)
    akar = ET.fromstring(mentah)
    if akar.find(f".//{W}abstractNum[@{W}abstractNumId='{ID_NOMOR}']") is None:
        # Seluruh abstractNum harus mendahului elemen num.
        posisi = len(akar.findall(f"{W}abstractNum"))
        akar.insert(posisi, _abstract_num())
        nomor = ET.SubElement(akar, f"{W}num")
        nomor.set(f"{W}numId", ID_NOMOR)
        _atur(nomor, "abstractNumId", val=ID_NOMOR)
    isi["word/numbering.xml"] = ET.tostring(akar, encoding="UTF-8", xml_declaration=True)

    gaya_mentah = isi["word/styles.xml"].decode("utf-8")
    akar_gaya = ET.fromstring(gaya_mentah)
    for tingkat in range(4):
        gaya = _gaya(akar_gaya, f"Heading{tingkat + 1}")
        if gaya is None:
            continue
        numpr = _anak(_anak(gaya, "pPr"), "numPr")
        _atur(numpr, "ilvl", val=str(tingkat))
        _atur(numpr, "numId", val=ID_NOMOR)
    isi["word/styles.xml"] = ET.tostring(akar_gaya, encoding="UTF-8", xml_declaration=True)


def _footer_xml() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:ftr {NS}><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
    ).encode("utf-8")


def _rujukan_footer() -> ET.Element:
    rujukan = ET.Element(f"{W}footerReference")
    rujukan.set(f"{W}type", "default")
    rujukan.set(R_ID, ID_FOOTER)
    return rujukan


def _sect_salin(asal: ET.Element, *, margin_nol: bool, format_nomor: str,
                mulai: str, pakai_footer: bool) -> ET.Element:
    sect = copy.deepcopy(asal)
    for tag in ("footerReference", "headerReference", "pgNumType"):
        for simpul in sect.findall(f"{W}{tag}"):
            sect.remove(simpul)
    if margin_nol:
        _atur(sect, "pgMar", left="0", right="0", top="0", bottom="0",
              header="0", footer="0", gutter="0")
    if pakai_footer:
        sect.insert(0, _rujukan_footer())
    _atur(sect, "pgNumType", fmt=format_nomor, start=mulai)
    return sect


def susun_seperti_pdf(docx: Path, sampul: Path | None) -> None:
    """Tambah sampul, daftar isi/gambar/tabel, dan nomor halaman pada .docx."""
    with zipfile.ZipFile(docx) as zin:
        isi = {nama: zin.read(nama) for nama in zin.namelist()}

    mentah = isi["word/document.xml"].decode("utf-8")
    for prefiks, uri in re.findall(r'xmlns:([A-Za-z0-9]+)="([^"]+)"', mentah):
        ET.register_namespace(prefiks, uri)

    akar = ET.fromstring(mentah)
    badan = akar.find(f"{W}body")
    sect_akhir = badan.find(f"{W}sectPr")
    if sect_akhir is None:
        mati("Struktur .docx tidak terduga: sectPr tidak ditemukan")

    # Bagian utama memakai angka arab mulai 1, sama seperti PDF.
    for simpul in sect_akhir.findall(f"{W}footerReference"):
        sect_akhir.remove(simpul)
    sect_akhir.insert(0, _rujukan_footer())
    _atur(sect_akhir, "pgNumType", fmt="decimal", start="1")

    # DAFTAR PUSTAKA dan LAMPIRAN bukan bab bernomor; pakai gaya tanpa nomor
    # agar tidak menambah hitungan bab.
    for paragraf in badan.findall(f"{W}p"):
        ppr = paragraf.find(f"{W}pPr")
        if ppr is None:
            continue
        gaya = ppr.find(f"{W}pStyle")
        if gaya is None or gaya.get(f"{W}val") != "Heading1":
            continue
        teks = "".join(simpul.text or "" for simpul in paragraf.iter(f"{W}t"))
        if teks.upper().startswith(("DAFTAR PUSTAKA", "LAMPIRAN")):
            gaya.set(f"{W}val", GAYA_TANPA_NOMOR)

    awalan: list[ET.Element] = []
    if sampul is not None:
        p_sampul = ET.fromstring(_p_sampul())
        _anak(p_sampul, "pPr").append(
            _sect_salin(sect_akhir, margin_nol=True, format_nomor="lowerRoman",
                        mulai="1", pakai_footer=False))
        awalan.append(p_sampul)

    # Judul pertama sudah berada di awal seksi baru; matikan page break-nya
    # agar tidak muncul halaman kosong sesudah sampul.
    p_isi = ET.fromstring(_p_judul("DAFTAR ISI"))
    _anak(_anak(p_isi, "pPr"), "pageBreakBefore").set(f"{W}val", "0")
    awalan.append(p_isi)
    awalan.append(ET.fromstring(_p_field(r' TOC \o "1-3" \h \z \u ')))
    # Field TOC yang kosong membuat Word menampilkan pesan galat, jadi daftar
    # gambar/tabel hanya dibuat bila keterangannya memang ada di naskah.
    for judul, gaya in (("DAFTAR GAMBAR", "ImageCaption"), ("DAFTAR TABEL", "TableCaption")):
        if f'w:val="{gaya}"' not in mentah:
            continue
        awalan.append(ET.fromstring(_p_judul(judul)))
        awalan.append(ET.fromstring(_p_field(rf' TOC \h \z \t "{gaya},1" ')))
    # Paragraf terakhir bagian awal memuat properti seksinya.
    _anak(awalan[-1], "pPr").append(
        _sect_salin(sect_akhir, margin_nol=False, format_nomor="lowerRoman",
                    mulai="2", pakai_footer=True))

    for posisi, simpul in enumerate(awalan):
        badan.insert(posisi, simpul)
    isi["word/document.xml"] = ET.tostring(akar, encoding="UTF-8", xml_declaration=True)

    # Tanpa penanda versi, Word membuka berkas dalam mode kompatibilitas dan
    # meminta konfirmasi pemutakhiran format setiap kali disimpan.
    if "word/settings.xml" in isi:
        pengaturan = isi["word/settings.xml"].decode("utf-8")
        if "compatibilityMode" not in pengaturan:
            pengaturan = pengaturan.replace(
                "</w:settings>",
                '<w:compat><w:compatSetting w:name="compatibilityMode" '
                'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>'
                "</w:compat></w:settings>",
            )
            isi["word/settings.xml"] = pengaturan.encode("utf-8")

    _pasang_penomoran(isi)
    isi["word/footer1.xml"] = _footer_xml()
    tambahan = (
        f'<Relationship Id="{ID_FOOTER}" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
    )
    if sampul is not None:
        isi["word/media/sampul.png"] = sampul.read_bytes()
        tambahan += (
            f'<Relationship Id="{ID_SAMPUL}" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/image" Target="media/sampul.png"/>'
        )
    isi["word/_rels/document.xml.rels"] = (
        isi["word/_rels/document.xml.rels"].decode("utf-8")
        .replace("</Relationships>", f"{tambahan}</Relationships>").encode("utf-8")
    )

    tipe = isi["[Content_Types].xml"].decode("utf-8")
    if "footer+xml" not in tipe:
        tipe = tipe.replace(
            "</Types>",
            '<Override PartName="/word/footer1.xml" ContentType="application/vnd.'
            'openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
    if 'Extension="png"' not in tipe:
        tipe = tipe.replace(
            "</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
    isi["[Content_Types].xml"] = tipe.encode("utf-8")

    with zipfile.ZipFile(docx, "w", zipfile.ZIP_DEFLATED) as zout:
        for nama, data in isi.items():
            zout.writestr(nama, data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--utama", type=Path, default=ROOT / "praskripsi.tex")
    parser.add_argument("--keluaran", type=Path, default=ROOT / "build" / "praskripsi.docx")
    args = parser.parse_args()

    if shutil.which("pandoc") is None:
        mati("Pandoc belum terpasang. macOS: brew install pandoc; Windows: unduh dari https://pandoc.org/installing.html")

    csl = ROOT / "assets" / "ieee.csl"
    if not csl.is_file():
        mati(f"Berkas gaya sitasi tidak ditemukan: {csl}")

    kerja = args.keluaran.parent / "docx"
    kerja.mkdir(parents=True, exist_ok=True)

    # Sampul diambil dari halaman pertama PDF; disiapkan lebih dulu karena
    # menentukan perlu tidaknya blok judul berupa teks.
    pdf = pdf_siap(args.utama, args.keluaran.with_suffix(".pdf"))
    sampul = render_sampul(pdf, kerja / "sampul.png") if pdf else None
    if sampul is None:
        print("PERINGATAN  Sampul gambar tidak tersedia; memakai blok judul teks")

    sumber = kerja / "sumber.tex"
    sumber.write_text(
        sumber_gabungan(metadata(), urutan_input(args.utama), blok_sampul=sampul is None),
        encoding="utf-8",
    )

    # Tahap 1: LaTeX -> Markdown, tanpa citeproc.
    antara = subprocess.run(
        ["pandoc", str(sumber), "--from=latex", "--to=markdown", "--wrap=preserve",
         f"--resource-path={ROOT}"],
        capture_output=True, text=True,
    )
    if antara.returncode != 0:
        mati(f"Pandoc gagal membaca sumber LaTeX:\n{antara.stderr.strip()}")

    # Tandai tempat daftar pustaka; tanpa ini citeproc menaruhnya di akhir
    # dokumen, yaitu sesudah lampiran.
    markdown = re.sub(
        r"^(#\s+DAFTAR PUSTAKA.*)$",
        r"\1\n\n::: {#refs}\n:::\n",
        antara.stdout,
        count=1,
        flags=re.M,
    )
    berkas_md = kerja / "sumber.md"
    berkas_md.write_text(markdown, encoding="utf-8")

    # Tahap 2: Markdown -> Word, dengan sitasi IEEE dan gaya pedoman.
    perintah = [
        "pandoc", str(berkas_md),
        "--from=markdown",
        "--citeproc",
        f"--bibliography={ROOT / 'bibliography' / 'references.bib'}",
        f"--csl={csl}",
        f"--reference-doc={reference_docx(kerja / 'reference.docx')}",
        f"--resource-path={ROOT}",
        "-o", str(args.keluaran),
    ]
    hasil = subprocess.run(perintah, capture_output=True, text=True)
    if hasil.returncode != 0:
        mati(f"Pandoc gagal menulis .docx:\n{hasil.stderr.strip()}")
    for aliran in (antara.stderr, hasil.stderr):
        if aliran.strip():
            print(aliran.strip())

    # Samakan dengan PDF: sampul, daftar isi/tabel, dan nomor halaman.
    susun_seperti_pdf(args.keluaran, sampul)
    print(f"LULUS  {args.keluaran}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
