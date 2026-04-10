from dataclasses import dataclass

try:
    from langchain_chroma import Chroma
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    Chroma = None  # type: ignore[assignment]
    OllamaEmbeddings = None  # type: ignore[assignment]

from app.core.settings import settings


@dataclass
class _SimpleDoc:
    page_content: str
    metadata: dict


class VectorStore:
    def __init__(self) -> None:
        if Chroma is not None and OllamaEmbeddings is not None:
            self.embeddings = OllamaEmbeddings(
                model=settings.embed_model,
                base_url=settings.ollama_base_url,
            )
            self.db = Chroma(
                collection_name=settings.chroma_collection,
                embedding_function=self.embeddings,
                persist_directory=settings.chroma_dir,
            )
            self._fallback_docs: list[_SimpleDoc] = []
        else:
            self.embeddings = None
            self.db = None
            self._fallback_docs = []

    def add_texts(self, texts: list[str], metadatas: list[dict], ids: list[str]) -> None:
        if self.db is not None:
            self.db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            return

        for text, metadata in zip(texts, metadatas, strict=False):
            self._fallback_docs.append(_SimpleDoc(page_content=text, metadata=metadata))

    def similarity_search(self, query: str, top_k: int = 4):
        if self.db is not None:
            return self.db.similarity_search(query, k=top_k)

        ranked = sorted(
            self._fallback_docs,
            key=lambda item: query.lower() in item.page_content.lower(),
            reverse=True,
        )
        return ranked[:top_k]


vector_store = VectorStore()
