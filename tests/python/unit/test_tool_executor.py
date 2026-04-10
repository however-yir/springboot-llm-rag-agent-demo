import pytest

pytest.importorskip("tenacity")

from app.tools.executor import tool_executor


def test_tool_executor_success_path():
    result = tool_executor.execute(
        "get_course_schedule",
        {"student_id": "20230001", "week": 9},
    )
    assert "courses" in result


def test_tool_executor_fallback_for_unknown_tool():
    result = tool_executor.execute("unknown_tool", {})
    assert result["status"] == "degraded"
