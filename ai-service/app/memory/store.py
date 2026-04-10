import json
import os
import threading
from typing import Any

from app.core.settings import settings


class SessionMemory:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data: dict[str, Any] = {"sessions": {}, "profiles": {}}
        self._load()

    def _load(self) -> None:
        path = settings.memory_path
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self._data = json.load(f)

    def _save(self) -> None:
        path = settings.memory_path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def append_session(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            self._data.setdefault("sessions", {}).setdefault(session_id, []).append(
                {"role": role, "content": content}
            )
            self._save()

    def get_recent_context(self, session_id: str, limit: int = 6) -> list[dict]:
        history = self._data.setdefault("sessions", {}).get(session_id, [])
        return history[-limit:]

    def get_or_create_profile(self, user_id: str) -> dict:
        with self._lock:
            profile = self._data.setdefault("profiles", {}).get(user_id)
            if profile is None:
                profile = {
                    "user_id": user_id,
                    "persona": "student",
                    "preferences": {"language": "zh-CN"},
                }
                self._data["profiles"][user_id] = profile
                self._save()
            return profile


session_memory = SessionMemory()
