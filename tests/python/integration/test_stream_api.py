import pytest
from fastapi.testclient import TestClient

pytest.importorskip("pydantic_settings")
pytest.importorskip("langgraph")
pytest.importorskip("langchain_ollama")

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
