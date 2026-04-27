---
name: pdf-to-word-docx
description: 'Convert PDF files to editable Word DOCX documents. Use for pdf to word conversion, docx export, OCR for scanned PDFs, and conversion quality checks.'
argument-hint: 'Source PDF path, optional output DOCX path, and OCR mode (auto, ask, or never)'
user-invocable: true
---

# PDF to Word DOCX Conversion

## When to Use
- Convert a PDF memo, report, or form into an editable `.docx` file
- Apply a repeatable conversion workflow with fallbacks
- Handle scanned or image-only PDFs using OCR before conversion

## Inputs
- Required: source PDF path
- Optional: output DOCX path
- Optional override: OCR behavior (`ocr=auto|ask|never`), default `auto`

## Decision Flow
1. Validate that the input file exists and ends in `.pdf`.
2. Detect source type:
   - Try extracting text from the PDF.
   - If text extraction is empty or unreadable, treat as scanned.
3. Pick conversion method in order:
   - Method A: LibreOffice headless conversion (best layout fidelity in many cases).
   - Method B: Python `pdf2docx` conversion (good fallback for text-heavy files).
   - Method C: OCR first, then Method A or B for scanned PDFs.
4. Validate output and report any formatting caveats.

## Procedure
1. Resolve paths:
   - Input: `<name>.pdf`
   - Default output: same directory, `<name>.docx`
2. Method A (LibreOffice):
   - Run: `soffice --headless --convert-to docx --outdir "<output_dir>" "<input.pdf>"`
   - If output exists and is non-empty, stop.
3. Method B (pdf2docx):
   - Ensure dependency is installed: `python -m pip install pdf2docx`
   - Convert with a Python snippet using `pdf2docx.Converter`.
4. Method C (OCR fallback):
   - If PDF is detected as scanned, run OCR automatically by default.
   - Run OCR to create searchable PDF: `ocrmypdf "<input.pdf>" "<tmp_searchable.pdf>"`
   - Convert the OCR output with Method A, then Method B if needed.
5. Validate results:
   - Output `.docx` exists and file size is greater than zero.
   - Document opens successfully.
   - At least one page has editable text.
   - Provide notes on expected cleanup (tables, headers, footnotes, page breaks).

## Completion Criteria
- A `.docx` file is produced at the requested output path.
- The file opens and contains editable text.
- The method used is reported.
- Known fidelity limits are reported when present.

## Failure Handling
- Missing tools: suggest installing `libreoffice`, `pdf2docx`, `ocrmypdf`, and `tesseract-ocr`.
- Protected PDF: request an unlocked/decrypted source.
- Poor layout fidelity: retry with a different method and report manual cleanup areas.

## Response Format
- Method selected and why
- Output path
- Validation outcome
- Cleanup recommendations