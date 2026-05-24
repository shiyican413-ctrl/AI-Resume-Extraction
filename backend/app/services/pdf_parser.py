from io import BytesIO

import pdfplumber
from pypdf import PdfReader

try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None


def parse_pdf_text(content: bytes) -> str:
    text_parts: list[str] = []

    if fitz is not None:
        try:
            with fitz.open(stream=content, filetype="pdf") as doc:
                for page in doc:
                    text_parts.append(page.get_text("text") or "")
        except Exception:
            text_parts = []
        text = "\n".join(text_parts).strip()
        if text:
            return text

    try:
        reader = PdfReader(BytesIO(content))
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        if text:
            return text
    except Exception:
        pass

    fallback_parts: list[str] = []
    with pdfplumber.open(BytesIO(content)) as pdf:
        for page in pdf.pages:
            fallback_parts.append(page.extract_text() or "")
    return "\n".join(fallback_parts).strip()
