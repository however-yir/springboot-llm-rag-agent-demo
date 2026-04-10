from app.models.schemas import SearchHit
from app.rag.vector_store import vector_store


class RetrieverService:
    def search(self, query: str, top_k: int = 4, department: str | None = None) -> list[SearchHit]:
        docs = vector_store.similarity_search(query=query, top_k=top_k)
        hits = []
        for doc in docs:
            if department and doc.metadata.get("department") != department:
                continue
            hits.append(
                SearchHit(
                    content=doc.page_content,
                    metadata=doc.metadata,
                )
            )
        return hits


retriever_service = RetrieverService()
