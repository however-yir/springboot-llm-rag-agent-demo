import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from threading import Lock
from typing import Any

from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.settings import settings
from app.tools.registry import tool_registry

logger = logging.getLogger(__name__)


@dataclass
class CircuitState:
    failures: int = 0
    opened_at: float | None = None


class ToolExecutor:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="tool-executor")
        self._states: dict[str, CircuitState] = {}
        self._lock = Lock()

    def execute(self, tool_name: str, action_input: dict[str, Any]) -> Any:
        if self._is_circuit_open(tool_name):
            return self._fallback(tool_name, "circuit_open")

        try:
            result = self._execute_with_retry(tool_name, action_input)
            self._reset_state(tool_name)
            return result
        except Exception as exc:
            self._mark_failure(tool_name)
            logger.warning("Tool %s execution degraded: %s", tool_name, exc)
            return self._fallback(tool_name, str(exc))

    @retry(
        stop=stop_after_attempt(settings.tool_retry_attempts + 1),
        wait=wait_fixed(settings.tool_retry_backoff_seconds),
        reraise=True,
    )
    def _execute_with_retry(self, tool_name: str, action_input: dict[str, Any]) -> Any:
        future = self._executor.submit(tool_registry.call, tool_name, action_input)
        try:
            return future.result(timeout=settings.tool_timeout_seconds)
        except TimeoutError as exc:
            raise RuntimeError(f"tool_timeout_{settings.tool_timeout_seconds}s") from exc

    def _state(self, tool_name: str) -> CircuitState:
        with self._lock:
            if tool_name not in self._states:
                self._states[tool_name] = CircuitState()
            return self._states[tool_name]

    def _is_circuit_open(self, tool_name: str) -> bool:
        state = self._state(tool_name)
        if state.opened_at is None:
            return False

        cooldown = settings.tool_circuit_breaker_cooldown_seconds
        if time.time() - state.opened_at >= cooldown:
            self._reset_state(tool_name)
            return False
        return True

    def _mark_failure(self, tool_name: str) -> None:
        state = self._state(tool_name)
        state.failures += 1
        if state.failures >= settings.tool_circuit_breaker_threshold:
            state.opened_at = time.time()

    def _reset_state(self, tool_name: str) -> None:
        state = self._state(tool_name)
        state.failures = 0
        state.opened_at = None

    def _fallback(self, tool_name: str, reason: str) -> dict[str, Any]:
        return {
            "status": "degraded",
            "tool": tool_name,
            "reason": reason,
            "message": "Tool execution downgraded, please retry or handoff to human operator.",
        }


tool_executor = ToolExecutor()
