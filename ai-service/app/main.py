import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router
from app.core.logging import configure_logging
from app.core.telemetry import configure_observability

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Campus/Enterprise AI Assistant API",
    version="0.2.0",
    description="Enterprise FastAPI + LangGraph service for RAG and ReAct agent",
)

configure_observability(app)
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "ValidationError",
            "message": "request validation failed",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": "InternalServerError",
            "message": str(exc),
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-service", "mode": "enterprise"}
