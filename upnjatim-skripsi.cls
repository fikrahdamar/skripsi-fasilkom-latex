% upnjatim-skripsi.cls -- template tidak resmi pra-skripsi/skripsi
% Fakultas Ilmu Komputer UPN "Veteran" Jawa Timur.
% Struktur diadaptasi dari filkomproposal.cls (template tidak resmi FILKOM UB)
% karya Pande Kadek Nathan Prabhaswara Sudiara Putra, LPPL 1.3c.
% Distributed under the LPPL 1.3c or later.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{upnjatim-skripsi}[2026/09/13 v0.1.0 Template tidak resmi skripsi Fasilkom UPN Veteran Jatim]

\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=upn,prefix=upn@}
\DeclareStringOption[praskripsi]{jenis}
\DeclareStringOption[putih]{sampul}
\DeclareBoolOption{ketat}
\ProcessKeyvalOptions*
\LoadClass[a4paper,12pt,oneside]{report}

\newif\ifupn@praskripsi
\def\upn@tmp{praskripsi}
\ifx\upn@jenis\upn@tmp
  \upn@praskripsitrue
\else
  \def\upn@tmp{skripsi}
  \ifx\upn@jenis\upn@tmp
    \upn@praskripsifalse
    \ClassWarningNoLine{upnjatim-skripsi}{jenis=skripsi baru menyediakan sampul; halaman pengesahan, persetujuan, orisinalitas, dan abstrak belum tersedia}
  \else
    \ClassError{upnjatim-skripsi}{Opsi jenis=\upn@jenis\space tidak dikenal}{Gunakan jenis=praskripsi atau jenis=skripsi.}
  \fi
\fi

\newif\ifupn@sampuloranye
\def\upn@tmp{oranye}
\ifx\upn@sampul\upn@tmp \upn@sampuloranyetrue \fi

\RequirePackage[indonesian]{babel}
\RequirePackage{fontspec}
\RequirePackage{csquotes}
\DeclareQuoteAlias[american]{english}{indonesian}
\RequirePackage[left=4cm,right=3cm,top=3cm,bottom=3cm,footskip=0.6cm]{geometry}
\RequirePackage{setspace}
\RequirePackage{indentfirst}
\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage{tikz}
\RequirePackage{titlesec}
\RequirePackage{titletoc}
\RequirePackage{caption}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{array}
\RequirePackage{tabularx}
\RequirePackage{multirow}
\RequirePackage{enumitem}
\RequirePackage[fleqn]{amsmath}
\RequirePackage{unicode-math}
\setmathfont{texgyretermes-math.otf}
% Times New Roman tidak punya glif ✓; ambil dari font matematika agar
% \checkmark juga aman dipakai di luar mode matematika (mis. tabel jadwal).
\AtBeginDocument{%
  \let\upn@checkmark\checkmark
  \renewcommand{\checkmark}{\ensuremath{\upn@checkmark}}}
\RequirePackage{listings}
\RequirePackage{xurl}
\RequirePackage{xkeyval}
\RequirePackage[backend=biber,style=ieee,language=english,autolang=none,
  isbn=false,doi=true,url=true,dashed=false]{biblatex}
\DeclareLanguageMapping{indonesian}{english}
\RequirePackage{hyperref}
\urlstyle{same}

% ---------------------------------------------------------------------------
% Font: Times New Roman (isi), Arial (sampul), Courier New (kode).
% Tanpa opsi ketat, font TeX Gyre dipakai sebagai pengganti (mis. Overleaf).
% ---------------------------------------------------------------------------
\newcommand{\upn@cadangan}[3]{%
  \ClassWarningNoLine{upnjatim-skripsi}{Font #2 tidak ditemukan; memakai #3 sebagai pengganti. Gunakan #2 untuk hasil akhir}%
  #1{#3}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,
    ItalicFont=*-italic,BoldItalicFont=*-bolditalic]}
\newcommand{\upn@pilihfont}[3]{%
  \IfFontExistsTF{#2}{#1{#2}}{%
    \ifupn@ketat
      \ClassError{upnjatim-skripsi}{Font #2 wajib saat opsi ketat dipakai}{Pasang #2 atau hapus opsi ketat.}%
    \else
      \upn@cadangan{#1}{#2}{#3}%
    \fi}}
\upn@pilihfont{\setmainfont}{Times New Roman}{texgyretermes}
\upn@pilihfont{\setmonofont}{Courier New}{texgyrecursor}
\upn@pilihfont{\newfontfamily\upn@fontsampul}{Arial}{texgyreheros}

% ---------------------------------------------------------------------------
% Metadata
% ---------------------------------------------------------------------------
\newcommand{\upn@judul}{}
\newcommand{\upn@nama}{}
\newcommand{\upn@npm}{}
\newcommand{\upn@pembimbingsatu}{}
\newcommand{\upn@pembimbingdua}{}
\newcommand{\upn@prodi}{Informatika}
\newcommand{\upn@fakultas}{Fakultas Ilmu Komputer}
\newcommand{\upn@universitas}{Universitas Pembangunan Nasional Veteran Jawa Timur}
\newcommand{\upn@kementerian}{Kementerian Pendidikan Tinggi, Sains, dan Teknologi}
\newcommand{\upn@kota}{Surabaya}
\newcommand{\upn@tahun}{\the\year}
\newcommand{\upn@logo}{assets/logo-upnjatim.png}

\define@key{upn}{judul}{\renewcommand{\upn@judul}{#1}}
\define@key{upn}{nama}{\renewcommand{\upn@nama}{#1}}
\define@key{upn}{npm}{\renewcommand{\upn@npm}{#1}}
\define@key{upn}{pembimbing-satu}{\renewcommand{\upn@pembimbingsatu}{#1}}
\define@key{upn}{pembimbing-dua}{\renewcommand{\upn@pembimbingdua}{#1}}
\define@key{upn}{program-studi}{\renewcommand{\upn@prodi}{#1}}
\define@key{upn}{fakultas}{\renewcommand{\upn@fakultas}{#1}}
\define@key{upn}{universitas}{\renewcommand{\upn@universitas}{#1}}
\define@key{upn}{kementerian}{\renewcommand{\upn@kementerian}{#1}}
\define@key{upn}{kota}{\renewcommand{\upn@kota}{#1}}
\define@key{upn}{tahun}{\renewcommand{\upn@tahun}{#1}}
\define@key{upn}{logo}{\renewcommand{\upn@logo}{#1}}
\newcommand{\upnsetup}[1]{\setkeys{upn}{#1}}

\newcommand{\upn@wajib}[2]{%
  \ifx#1\@empty
    \ClassError{upnjatim-skripsi}{Metadata #2 belum diisi}{Isi kunci #2 pada metadata.tex.}%
  \fi}
\AtBeginDocument{%
  \upn@wajib{\upn@judul}{judul}%
  \upn@wajib{\upn@nama}{nama}%
  \upn@wajib{\upn@npm}{npm}%
  \upn@wajib{\upn@pembimbingsatu}{pembimbing-satu}%
  \hypersetup{hidelinks,unicode,pdftitle={\upn@judul},pdfauthor={\upn@nama}}%
}

% ---------------------------------------------------------------------------
% Tata letak isi: 12 pt, spasi 1,5 baris Word (20,7 pt), paragraf +6 pt,
% indentasi baris pertama 1,27 cm.
% ---------------------------------------------------------------------------
\setstretch{1.43}
\setlength{\parindent}{1.27cm}
\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{2em}
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\setlength{\mathindent}{1.27cm}

\setlist{nosep}
\setlist[enumerate]{leftmargin=1.25cm,labelwidth=0.6cm,labelsep=0pt,align=left}
\setlist[itemize]{leftmargin=1.25cm,labelwidth=0.6cm,labelsep=0pt,align=left}

% ---------------------------------------------------------------------------
% Penomoran: BAB I, subbab 1.1., gambar/tabel/persamaan 2.1
% ---------------------------------------------------------------------------
\renewcommand{\thechapter}{\Roman{chapter}}
\renewcommand{\thesection}{\arabic{chapter}.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\thesubsection.\arabic{subsubsection}}
\renewcommand{\thefigure}{\arabic{chapter}.\arabic{figure}}
\renewcommand{\thetable}{\arabic{chapter}.\arabic{table}}
\renewcommand{\theequation}{\arabic{chapter}.\arabic{equation}}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{2}

% 16,8 pt x setstretch 1,43 = jarak baris judul bab 24 pt (Pedoman hlm. 31).
\newcommand{\upn@fontbab}{\fontsize{14pt}{16.8pt}\selectfont\setlength{\parskip}{0pt}}
\newcommand{\upn@kapital}{\MakeUppercase}
\titleformat{\chapter}[display]
  {\centering\bfseries\upn@fontbab}{BAB \thechapter}{0pt}{\MakeUppercase}
\titleformat{name=\chapter,numberless}[block]
  {\centering\bfseries\upn@fontbab}{}{0pt}{\upn@kapital}
% Dikalibrasi terhadap Pedoman hlm. 31: puncak "BAB I" +-31 mm, judul ke teks 41,6 pt.
\titlespacing*{\chapter}{0pt}{-22.7pt}{14pt}
\titlespacing*{name=\chapter,numberless}{0pt}{-22.7pt}{14pt}
\titleformat{\section}[hang]
  {\bfseries\normalsize}{\makebox[1.27cm][l]{\thesection.}}{0pt}{}
\titleformat{\subsection}[hang]
  {\bfseries\normalsize}{\thesubsection.}{0.5em}{}
\titleformat{\subsubsection}[hang]
  {\bfseries\normalsize}{\thesubsubsection.}{0.5em}{}
% Ditambah \parskip 6 pt: sebelum subbab +12 pt, sub-subbab +9 pt (Pedoman hlm. 31-38).
\titlespacing*{\section}{0pt}{6pt}{0pt}
\titlespacing*{\subsection}{0pt}{3pt}{0pt}
\titlespacing*{\subsubsection}{0pt}{3pt}{0pt}

% ---------------------------------------------------------------------------
% Daftar isi, gambar, tabel
% ---------------------------------------------------------------------------
\newcommand{\upn@titik}{\titlerule*[0.4em]{.}}
% Makro terakhir pada format entri menerima judul sebagai argumen.
\titlecontents{chapter}[0pt]{\bfseries}
  {BAB \thecontentslabel\space\MakeUppercase}{\MakeUppercase}{\upn@titik\contentspage}
\titlecontents{section}[1.9cm]{}
  {\contentslabel[\thecontentslabel.]{1.27cm}}{}{\upn@titik\contentspage}
\titlecontents{subsection}[3.2cm]{}
  {\contentslabel[\thecontentslabel.]{1.3cm}}{}{\upn@titik\contentspage}
\titlecontents{figure}[2.5cm]{}
  {\contentslabel[\textbf{\figurename~\thecontentslabel}]{2.5cm}}{}{\upn@titik\contentspage}
\titlecontents{table}[2.2cm]{}
  {\contentslabel[\textbf{\tablename~\thecontentslabel}]{2.2cm}}{}{\upn@titik\contentspage}

\newcommand{\upn@daftar}[2]{% #1 judul, #2 ekstensi berkas
  \clearpage
  \chapter*{#1}%
  \phantomsection
  \addcontentsline{toc}{chapter}{\MakeUppercase{#1}}%
  \begingroup
  \setlength{\parskip}{0pt}%
  \@starttoc{#2}%
  \endgroup
  \clearpage}
\newcommand{\daftarisi}{\upn@daftar{Daftar Isi}{toc}}
\newcommand{\daftargambar}{\upn@daftar{Daftar Gambar}{lof}}
\newcommand{\daftartabel}{\upn@daftar{Daftar Tabel}{lot}}

% ---------------------------------------------------------------------------
% Gambar, tabel, kode sumber
% ---------------------------------------------------------------------------
\captionsetup{font={normalsize,bf},labelsep=space,skip=6pt}
\captionsetup[table]{position=top,justification=raggedright,singlelinecheck=false}
\captionsetup[figure]{position=bottom,justification=centering}
\newcommand{\sumber}[1]{%
  \par\vspace{3pt}{\centering\fontsize{11pt}{13pt}\selectfont Sumber: #1\par}}

\DeclareCaptionFont{upnkode}{\fontsize{9pt}{11pt}\selectfont}
\captionsetup[lstlisting]{font=upnkode,labelfont=bf,labelsep=colon,
  justification=raggedright,singlelinecheck=false,skip=3pt}
\renewcommand{\lstlistingname}{Algoritme}
\lstset{
  basicstyle=\setstretch{1}\ttfamily\fontsize{9pt}{11pt}\selectfont,
  numberstyle=\ttfamily\fontsize{9pt}{11pt}\selectfont,
  numbers=left, numbersep=8pt, xleftmargin=2em, framexleftmargin=2em,
  frame=single, breaklines=true, columns=fullflexible, keepspaces=true,
  showstringspaces=false, tabsize=2, captionpos=t, numberbychapter=false,
  aboveskip=6pt, belowskip=6pt
}

% ---------------------------------------------------------------------------
% Daftar pustaka: IEEE, spasi tunggal
% ---------------------------------------------------------------------------
% Bahasa aktif babel "indonesian" dipetakan ke lbx english; isi keduanya.
\DefineBibliographyStrings{english}{
  and={dan}, in={dalam}, url={Tersedia}, urlseen={Diakses},
}
\DefineBibliographyStrings{indonesian}{
  and={dan}, in={dalam}, url={Tersedia}, urlseen={Diakses},
}
% biblatex-ieee mengubah judul ke sentence case; pertahankan kapitalisasi
% sesuai berkas .bib (contoh Pedoman hlm. 23) agar judul Indonesia tidak rusak.
\DeclareFieldFormat{sentencecase}{#1}
\setlength{\bibitemsep}{6pt}
% Judul dicetak di luar grup spasi tunggal agar posisinya sama dengan judul bab.
\newcommand{\daftarpustaka}{%
  \clearpage
  \chapter*{Daftar Pustaka}%
  \phantomsection
  \addcontentsline{toc}{chapter}{DAFTAR PUSTAKA}%
  \begingroup
  \setstretch{1}%
  \printbibliography[heading=none]%
  \endgroup}

% ---------------------------------------------------------------------------
% Bagian dokumen
% ---------------------------------------------------------------------------
\newcommand{\bagianutama}{\clearpage\pagenumbering{arabic}}

\newcounter{lampiran}
\newcommand{\lampiran}[1]{%
  \clearpage
  \refstepcounter{lampiran}%
  \edef\upn@nolampiran{\arabic{lampiran}}%
  % \\ tidak boleh berada di dalam \MakeUppercase; kapitalkan per baris.
  \begingroup
  \let\upn@kapital\@firstofone
  \chapter*{\MakeUppercase{Lampiran \upn@nolampiran}\\\MakeUppercase{#1}}%
  \endgroup
  \phantomsection
  \addcontentsline{toc}{chapter}{LAMPIRAN \upn@nolampiran\space\MakeUppercase{#1}}%
  \setcounter{figure}{0}\setcounter{table}{0}\setcounter{equation}{0}%
  \renewcommand{\thefigure}{L\arabic{lampiran}.\arabic{figure}}%
  \renewcommand{\thetable}{L\arabic{lampiran}.\arabic{table}}%
  \renewcommand{\theequation}{L\arabic{lampiran}.\arabic{equation}}}

% ---------------------------------------------------------------------------
% Sampul (Pedoman 2025 hlm. 8-10): pita oranye 10-20 mm, logo 4 x 4 cm pada
% 20 mm dari kiri dan 30 mm dari atas, pita kuning 80-85 mm, teks Arial rata
% kiri pada 35 mm dari kiri.
% ---------------------------------------------------------------------------
\definecolor{upnoranye}{HTML}{FF914D}
\definecolor{upnkuning}{HTML}{F4FF00}

\newcommand{\upn@labeljenis}{%
  \ifupn@praskripsi PRA-\textbf{SKRIPSI}\else\textbf{SKRIPSI}\fi}

\newcommand{\buatsampul}{%
  \clearpage
  \pagenumbering{roman}%
  \thispagestyle{empty}%
  \hypersetup{pageanchor=false}%
  \IfFileExists{\upn@logo}{}{%
    \ClassError{upnjatim-skripsi}{Logo tidak ditemukan: \upn@logo}{Periksa kunci logo pada metadata.tex.}}%
  \begin{tikzpicture}[remember picture,overlay,x=1mm,y=-1mm,
      shift={(current page.north west)}]
    \ifupn@sampuloranye
      \fill[upnoranye] (0,85) rectangle (210,297);
    \fi
    \fill[upnoranye] (0,10) rectangle (210,20);
    \fill[upnkuning] (0,80) rectangle (210,85);
    \node[anchor=north west,inner sep=0pt] at (20,30)
      {\includegraphics[width=4cm,height=4cm,keepaspectratio]{\upn@logo}};
    \node[anchor=north west,inner sep=0pt,text width=140mm,align=left] at (35,96)
      {\upn@fontsampul
       \ifupn@sampuloranye\color{white}\fi
       \setstretch{1}%
       \hyphenpenalty=10000\exhyphenpenalty=10000
       \setlength{\parskip}{0pt}%
       \raggedright
       {\fontsize{14pt}{17pt}\selectfont\upn@labeljenis\par}
       \vspace{8mm}
       {\fontsize{18pt}{26pt}\selectfont\bfseries\MakeUppercase{\upn@judul}\par}
       \vspace{20mm}
       {\fontsize{14pt}{22pt}\selectfont
        \textbf{\MakeUppercase{\upn@nama}}\par
        NPM \upn@npm\par
        \vspace{11mm}
        \textbf{DOSEN PEMBIMBING}\par
        \fontsize{14pt}{19pt}\selectfont
        \upn@pembimbingsatu\par
        \ifx\upn@pembimbingdua\@empty\else\upn@pembimbingdua\par\fi}};
    \node[anchor=north west,inner sep=0pt,text width=150mm,align=left] at (35,236)
      {\upn@fontsampul
       \ifupn@sampuloranye\color{white}\fi
       \setstretch{1}%
       \raggedright
       \fontsize{12pt}{18.5pt}\selectfont\bfseries
       \MakeUppercase{\upn@kementerian}\par
       \MakeUppercase{\upn@universitas}\par
       \MakeUppercase{\upn@fakultas}\par
       \MakeUppercase{Program Studi \upn@prodi}\par
       \MakeUppercase{\upn@kota}\par
       \upn@tahun};
  \end{tikzpicture}%
  \null
  \clearpage
  \hypersetup{pageanchor=true}%
  \setcounter{page}{2}}

\endinput
