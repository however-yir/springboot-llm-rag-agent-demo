from app.tools.registry import tool_registry


def test_tools_registered():
    specs = tool_registry.get_tool_specs()
    names = {item["name"] for item in specs}
    assert "get_course_schedule" in names
    assert "submit_repair_ticket" in names
    assert "generate_weekly_report" in names


def test_repair_ticket_tool():
    result = tool_registry.call(
        "submit_repair_ticket",
        {"location": "Dorm A-302", "issue": "Air conditioner not cooling"},
    )
    assert result["status"] == "submitted"
    assert result["ticket_id"].startswith("RP-")
