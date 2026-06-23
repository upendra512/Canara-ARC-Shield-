"""Layer 0 OCR and parsing node.

This implementation stays offline.

It supports:
1. raw_text already present in state.
2. normal text-like files.
3. text PDFs when pypdf is installed.
4. simple .eml email files using Python's standard library.
"""

from __future__ import annotations

from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any

from graph.state import RegulatoryIntakeState


TEXT_EXTENSIONS = {".csv", ".html", ".json", ".md", ".txt", ".xml"}


def read_text_file(path: Path) -> str:
    """Read a text file with common encoding fallbacks."""

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return path.read_text(errors="ignore")


def read_pdf_text(path: Path) -> str:
    """Extract selectable text from a PDF using local pypdf."""

    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return ""

    reader = PdfReader(str(path))
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text is not None and text.strip() != "":
            pages.append(text.strip())

    return "\n\n".join(pages)


def read_email_text(path: Path) -> str:
    """Extract plain text from an .eml file."""

    with path.open("rb") as file:
        message = BytesParser(policy=policy.default).parse(file)

    parts = []

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                parts.append(part.get_content())
    elif message.get_content_type() == "text/plain":
        parts.append(message.get_content())

    return "\n\n".join(parts)


def ocr_node(state: RegulatoryIntakeState) -> dict[str, Any]:
    """Extract raw text from the validated document."""

    existing_text = state.get("raw_text", "").strip()
    confidence = dict(state.get("confidence", {}))

    if existing_text != "":
        confidence["extraction_confidence"] = 1.0
        return {
            "raw_text": existing_text,
            "confidence": confidence,
            "status": "ocr_completed_from_payload",
        }

    file_path = state.get("file_path", "").strip()
    if file_path == "":
        confidence["extraction_confidence"] = 0.0
        return {
            "raw_text": "",
            "confidence": confidence,
            "status": "ocr_skipped_no_file",
        }

    path = Path(file_path)
    if not path.exists() or not path.is_file():
        confidence["extraction_confidence"] = 0.0
        return {
            "raw_text": "",
            "confidence": confidence,
            "status": "ocr_failed_file_not_found",
        }

    extension = path.suffix.lower()

    if extension in TEXT_EXTENSIONS:
        raw_text = read_text_file(path)
    elif extension == ".pdf":
        raw_text = read_pdf_text(path)
    elif extension == ".eml":
        raw_text = read_email_text(path)
    else:
        raw_text = ""

    raw_text = raw_text.strip()

    if raw_text != "":
        status = "ocr_completed"
        confidence["extraction_confidence"] = 0.9
    else:
        status = "ocr_failed_no_text_extracted"
        confidence["extraction_confidence"] = 0.1

    return {
        "raw_text": raw_text,
        "confidence": confidence,
        "status": status,
    }
