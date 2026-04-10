from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:7b"
    embed_model: str = "nomic-embed-text"

    chroma_dir: str = "./data/chroma"
    chroma_collection: str = "campus_docs"
    max_steps: int = 5

    memory_path: str = "./data/session_memory.json"
    langgraph_state_db: str = "./data/langgraph_state.db"

    tool_timeout_seconds: int = 8
    tool_retry_attempts: int = 2
    tool_retry_backoff_seconds: float = 0.4
    tool_circuit_breaker_threshold: int = 3
    tool_circuit_breaker_cooldown_seconds: int = 30

    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    service_name: str = "rag-react-ai-service"

    sse_chunk_size: int = 14

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
