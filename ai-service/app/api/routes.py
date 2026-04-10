import asyncio
import json
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.agent.react_graph import react_agent_service
from app.core.settings import settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
    ToolDescriptor,
    UploadResponse,
)
from app.rag.ingestion import ingestion_service
from app.rag.retriever import retriever_service
from app.tools.registry import tool_registry

router = APIRouter()


@router.get("/tools", response_model=list[ToolDescriptor])
def list_tools() -> list[ToolDescriptor]:
    return [ToolDescriptor(**tool) for tool in tool_registry.get_tool_specs()]


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    department: str | None = Form(default=None),
) -> UploadResponse:
    try:
        payload = await file.read()
        doc_id, chunks = ingestion_service.ingest_document(
            filename=file.filename,
            payload=payload,
            department=department,
        )
        return UploadResponse(doc_id=doc_id, chunks_indexed=chunks, filename=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/rag/search", response_model=SearchResponse)
def rag_search(request: SearchRequest) -> SearchResponse:
    hits = retriever_service.search(
        query=request.query,
        top_k=request.top_k,
        department=request.department,
    )
    return SearchResponse(query=request.query, hits=hits)


@router.post("/agent/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return react_agent_service.run(request)


def _sse_event(event: str, data: dict[str, Any] | str) -> str:
    if isinstance(data, dict):
        payload = json.dumps(data, ensure_ascii=False)
    else:
        payload = data
    return f"event: {event}\ndata: {payload}\n\n"


def _chunk_text(text: str, size: int) -> list[str]:
    if size <= 0:
        return [text]
    return [text[index:index + size] for index in range(0, len(text), size)]


@router.post("/agent/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    response = await asyncio.to_thread(react_agent_service.run, request)

    async def event_generator():
        for step in response.trace:
            yield _sse_event("trace", step.model_dump())
            await asyncio.sleep(0)

        for token in _chunk_text(response.answer, settings.sse_chunk_size):
            yield _sse_event("token", {"text": token})
            await asyncio.sleep(0.02)

        yield _sse_event("done", response.model_dump())

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
