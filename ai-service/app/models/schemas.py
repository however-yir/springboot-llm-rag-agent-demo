from typing import Any

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    doc_id: str
    chunks_indexed: int
    filename: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 4
    department: str | None = None


class SearchHit(BaseModel):
    content: str
    metadata: dict[str, Any]


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHit]


class ChatRequest(BaseModel):
    user_id: str = Field(default="demo-user")
    session_id: str = Field(default="session-001")
    message: str
    department: str | None = None


class AgentStep(BaseModel):
    step: int
    thought: str
    action: str
    action_input: dict[str, Any]
    observation: Any


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    trace: list[AgentStep]
    retrieval_preview: list[SearchHit]


class ToolDescriptor(BaseModel):
    name: str
    description: str
    required_params: list[str]
