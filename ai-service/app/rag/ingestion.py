import io
import uuid

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    class RecursiveCharacterTextSplitter:  # type: ignore[override]
        """Fallback splitter used for lightweight local testing."""

        def __init__(self, chunk_size: int, chunk_overlap: int, separators: list[str] | None = None) -> None:
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

        def split_text(self, text: str) -> list[str]:
            if not text:
                return []
            chunks: list[str] = []
            cursor = 0
            while cursor < len(text):
                end = min(cursor + self.chunk_size, len(text))
                chunks.append(text[cursor:end])
                if end == len(text):
                    break
                cursor = max(0, end - self.chunk_overlap)
            return chunks


class IngestionService:
    def __init__(self) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=120,
            separators=["\n\n", "\n", "。", ".", " "],
        )

    def extract_text(self, filename: str, payload: bytes) -> str:
        lower = filename.lower()
        if lower.endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(payload))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if lower.endswith(".docx"):
            from docx import Document

            document = Document(io.BytesIO(payload))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        if lower.endswith(".md") or lower.endswith(".txt"):
            return payload.decode("utf-8", errors="ignore")
        raise ValueError("Unsupported file type. Only PDF/DOCX/MD/TXT are supported.")

    def ingest_document(self, filename: str, payload: bytes, department: str | None = None) -> tuple[str, int]:
        text = self.extract_text(filename=filename, payload=payload)
        chunks = self.splitter.split_text(text)

        doc_id = str(uuid.uuid4())
        ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "doc_id": doc_id,
                "chunk_id": i,
                "filename": filename,
                "department": department or "general",
            }
            for i in range(len(chunks))
        ]

        if chunks:
            from app.rag.vector_store import vector_store

            vector_store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
        return doc_id, len(chunks)


ingestion_service = IngestionService()
