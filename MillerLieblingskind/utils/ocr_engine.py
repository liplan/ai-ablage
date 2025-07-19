"""OCR engine for converting PDF files to text."""

from typing import List

try:
    from pdf2image import convert_from_path
    import pytesseract
    from pytesseract import TesseractNotFoundError
except ImportError:
    convert_from_path = None
    pytesseract = None
    TesseractNotFoundError = RuntimeError


def pdf_to_text(pdf_path: str) -> str:
    """Convert a PDF file to text using OCR."""
    if convert_from_path is None or pytesseract is None:
        raise ImportError("pdf2image and pytesseract must be installed for OCR")

    pages: List[str] = []
    images = convert_from_path(pdf_path)
    for image in images:
        try:
            page_text = pytesseract.image_to_string(image, lang="deu")
        except TesseractNotFoundError as exc:
            raise RuntimeError(
                "Tesseract executable not found. Install tesseract-ocr and make sure it is in your PATH."
            ) from exc
        pages.append(page_text)
    return "\n".join(pages)
