LATEXMK ?= latexmk
OUT := build

.PHONY: all praskripsi docx watch check clean

all: praskripsi

praskripsi:
	$(LATEXMK) -outdir=$(OUT) praskripsi.tex

docx:
	python3 scripts/build_docx.py

watch:
	$(LATEXMK) -pvc -outdir=$(OUT) praskripsi.tex

check: praskripsi
	python3 scripts/check_pdf.py $(OUT)/praskripsi.pdf --log $(OUT)/praskripsi.log

clean:
	$(LATEXMK) -C -outdir=$(OUT) praskripsi.tex
	rm -rf $(OUT)
