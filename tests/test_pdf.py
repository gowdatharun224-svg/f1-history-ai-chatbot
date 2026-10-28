def test_pdf_exists_and_extracts():
    from pdf_retrieval import PDFKnowledgeBase
    kb = PDFKnowledgeBase()
    assert kb.raw_text != "" or not kb.chunks
    assert "575" in kb.raw_text or "2023" in kb.raw_text

def test_pdf_points_2023():
    from pdf_retrieval import pdf_points_2023
    text = pdf_points_2023()
    assert "575" in text
