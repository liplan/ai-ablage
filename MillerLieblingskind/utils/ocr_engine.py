"""OCR engine for converting PDF files to text."""

from typing import List
import os

try:
    from pdf2image import convert_from_path
    import pytesseract
    from pytesseract import TesseractNotFoundError, TesseractError
except ImportError:
    convert_from_path = None
    pytesseract = None
    TesseractNotFoundError = RuntimeError


DEFAULT_TESSDATA_PATHS = [
    "/usr/share/tesseract-ocr/5/tessdata",
    "/usr/share/tesseract-ocr/4.00/tessdata",
    "/usr/local/share/tessdata",
    "/opt/homebrew/share/tessdata",
]


def _ensure_tessdata_prefix() -> None:
    """Attempt to set TESSDATA_PREFIX if it is missing."""
    if "TESSDATA_PREFIX" in os.environ:
        return
    for path in DEFAULT_TESSDATA_PATHS:
        if os.path.isdir(path):
            os.environ["TESSDATA_PREFIX"] = path
            break


def pdf_to_text(pdf_path: str) -> str:
    """Convert a PDF file to text using OCR."""
    if convert_from_path is None or pytesseract is None:
        raise ImportError("pdf2image and pytesseract must be installed for OCR")

    _ensure_tessdata_prefix()

    pages: List[str] = []
    images = convert_from_path(pdf_path)
    for image in images:
        try:
            page_text = pytesseract.image_to_string(image, lang="deu")
        except TesseractNotFoundError as exc:
            raise RuntimeError(
                "Tesseract executable not found. Install tesseract-ocr and make sure it is in your PATH."
            ) from exc
        except TesseractError as exc:
            raise RuntimeError(
                "Tesseract failed to run. Ensure the 'deu' language data is installed and TESSDATA_PREFIX points to the tessdata directory."
            ) from exc
        pages.append(page_text)
    return "\n".join(pages)
