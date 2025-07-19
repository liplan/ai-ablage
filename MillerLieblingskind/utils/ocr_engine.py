"""OCR engine for converting PDF files to text."""

from typing import List
import os
import logging

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
    "/usr/share/tesseract-ocr/tessdata",
    "/usr/share/tessdata",
    "/usr/local/share/tessdata",
    "/opt/homebrew/share/tessdata",
]

# language used for OCR
LANGUAGE = "deu"


def _ensure_tessdata_prefix() -> None:
    """Ensure ``TESSDATA_PREFIX`` points to a directory containing the
    requested language data."""

    lang_file = f"{LANGUAGE}.traineddata"

    # collect possible directories from the current environment and defaults
    candidates = []
    if "TESSDATA_PREFIX" in os.environ:
        candidates.append(os.environ["TESSDATA_PREFIX"])
    candidates.extend(DEFAULT_TESSDATA_PATHS)

    for path in candidates:
        if not path:
            continue
        if os.path.isfile(os.path.join(path, lang_file)):
            os.environ["TESSDATA_PREFIX"] = path
            return

    logging.error("Could not find %s in known tessdata directories: %s", lang_file, candidates)
    raise RuntimeError(
        f"Language data '{lang_file}' not found. Install the appropriate"
        " tesseract language package and set TESSDATA_PREFIX accordingly."
    )


def pdf_to_text(pdf_path: str) -> str:
    """Convert a PDF file to text using OCR."""
    if convert_from_path is None or pytesseract is None:
        raise ImportError("pdf2image and pytesseract must be installed for OCR")

    _ensure_tessdata_prefix()

    pages: List[str] = []
    images = convert_from_path(pdf_path)
    for image in images:
        try:
            page_text = pytesseract.image_to_string(image, lang=LANGUAGE)
        except TesseractNotFoundError as exc:
            raise RuntimeError(
                "Tesseract executable not found. Install tesseract-ocr and make sure it is in your PATH."
            ) from exc
        except TesseractError as exc:
            raise RuntimeError(
                f"Tesseract failed to run. Ensure the '{LANGUAGE}' language data is installed and TESSDATA_PREFIX points to the tessdata directory."
            ) from exc
        pages.append(page_text)
    return "\n".join(pages)
