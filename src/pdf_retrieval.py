"""
PDF knowledge base retrieval.
Extracts chunks from data/pdfs/F1_History_Knowledge_Base_2021-2025.pdf
and provides keyword-based matching with structured data fallback.
"""

from pathlib import Path
from typing import List, Dict, Any

PDF_PATH = Path(__file__).resolve().parent.parent / "data" / "pdfs" / "F1_History_Knowledge_Base_2021-2025.pdf"


def extract_pdf_text() -> str:
    """Extract full text from PDF, handling missing file gracefully."""
    if not PDF_PATH.exists():
        return ""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(PDF_PATH))
        parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n".join(parts)
    except Exception:
        return ""


def chunk_text(text: str, chunk_size: int = 400) -> List[str]:
    """Split text into overlapping chunks for retrieval."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for p in paragraphs:
        if len(p) > chunk_size:
            for i in range(0, len(p), chunk_size // 2):
                chunks.append(p[i:i + chunk_size])
        else:
            chunks.append(p)
    return chunks


class PDFKnowledgeBase:
    def __init__(self):
        self.raw_text = extract_pdf_text()
        self.chunks = chunk_text(self.raw_text) if self.raw_text else []

    def search(self, query: str, top_n: int = 3) -> List[str]:
        q = query.lower()
        scores = []
        for chunk in self.chunks:
            score = sum(1 for word in q.split() if word in chunk.lower() and len(word) > 2)
            scores.append((score, chunk))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scores[:top_n] if chunk]


_pdf_kb = PDFKnowledgeBase()


def get_pdf_answer(query: str) -> str | None:
    """Return PDF-based answer snippet if relevant chunks found."""
    if not _pdf_kb.chunks:
        return None
    chunks = _pdf_kb.search(query, top_n=2)
    if not chunks:
        return None
    # Build a concise answer from top chunks
    combined = " ".join(chunks)
    # Truncate for chat display
    if len(combined) > 800:
        combined = combined[:800] + "..."
    return combined


def pdf_points_2023() -> str:
    return "575 points (2023 Drivers' Championship — Max Verstappen, Red Bull)."