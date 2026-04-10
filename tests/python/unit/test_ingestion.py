from app.rag.ingestion import IngestionService


def test_extract_text_from_markdown_bytes():
    service = IngestionService()
    content = service.extract_text("sample.md", b"# Title\nhello world")
    assert "Title" in content
    assert "hello world" in content
