from datetime import datetime, timezone
from typing import Any


class ToolRegistry:
    def __init__(self) -> None:
        self.tools = {
            "get_course_schedule": {
                "description": "查询某位学生某周的课表。",
                "required_params": ["student_id", "week"],
                "fn": self.get_course_schedule,
            },
            "submit_repair_ticket": {
                "description": "提交宿舍或办公设备报修工单。",
                "required_params": ["location", "issue"],
                "fn": self.submit_repair_ticket,
            },
            "generate_weekly_report": {
                "description": "生成本周学习/工作周报摘要。",
                "required_params": ["owner", "highlights"],
                "fn": self.generate_weekly_report,
            },
        }

    def get_tool_specs(self) -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "description": value["description"],
                "required_params": value["required_params"],
            }
            for name, value in self.tools.items()
        ]

    def call(self, name: str, params: dict[str, Any]) -> Any:
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        return self.tools[name]["fn"](**params)

    def get_course_schedule(self, student_id: str, week: int) -> dict[str, Any]:
        return {
            "student_id": student_id,
            "week": week,
            "courses": [
                {"day": "Mon", "slot": "1-2", "name": "Data Structures"},
                {"day": "Wed", "slot": "3-4", "name": "Software Engineering"},
                {"day": "Fri", "slot": "5-6", "name": "Machine Learning"},
            ],
        }

    def submit_repair_ticket(self, location: str, issue: str) -> dict[str, Any]:
        ticket_id = f"RP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        return {
            "ticket_id": ticket_id,
            "location": location,
            "issue": issue,
            "status": "submitted",
        }

    def generate_weekly_report(self, owner: str, highlights: list[str]) -> dict[str, Any]:
        return {
            "owner": owner,
            "summary": "; ".join(highlights),
            "next_week_focus": "Continue deepening practical implementation and validation.",
        }


tool_registry = ToolRegistry()
