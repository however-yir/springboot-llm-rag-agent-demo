import json
import logging
import os
import re
from typing import Any, TypedDict

try:
    from langgraph.graph import END, StateGraph
except ImportError:
    END = "__end__"  # type: ignore[assignment]
    StateGraph = None  # type: ignore[assignment]

from app.core.settings import settings
from app.memory.store import session_memory
from app.models.schemas import AgentStep, ChatRequest, ChatResponse, SearchHit
from app.rag.retriever import retriever_service
from app.tools.executor import tool_executor
from app.tools.registry import tool_registry

logger = logging.getLogger(__name__)


class _SimpleLlmResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class _FallbackLLM:
    def invoke(self, _: str) -> _SimpleLlmResponse:
        fallback_json = {
            "thought": "Local fallback model used because ChatOllama dependency is unavailable.",
            "action": "finish",
            "action_input": {},
            "answer": "当前运行于轻量降级模式，建议在完整依赖环境下获得更高质量回答。",
        }
        return _SimpleLlmResponse(json.dumps(fallback_json, ensure_ascii=False))


class AgentState(TypedDict, total=False):
    user_id: str
    session_id: str
    question: str
    department: str | None
    step: int
    action: str
    action_input: dict[str, Any]
    thought: str
    answer_candidate: str
    final_answer: str
    retrieved_preview: list[SearchHit]
    trace: list[AgentStep]
    observations: list[str]
    context: str


class ReActAgentService:
    def __init__(self) -> None:
        self.llm = self._init_llm()
        self.checkpointer = self._init_checkpointer()
        self.graph = self._build_graph()

    def _init_llm(self):
        try:
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=settings.llm_model,
                base_url=settings.ollama_base_url,
                temperature=0.2,
            )
        except Exception as exc:
            logger.warning("ChatOllama is unavailable, fallback LLM will be used: %s", exc)
            return _FallbackLLM()

    def _init_checkpointer(self):
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver

            os.makedirs(os.path.dirname(settings.langgraph_state_db) or ".", exist_ok=True)
            return SqliteSaver.from_conn_string(settings.langgraph_state_db)
        except Exception as exc:
            logger.warning("LangGraph checkpoint is disabled: %s", exc)
            return None

    def _build_graph(self):
        if StateGraph is None:
            return None

        builder = StateGraph(AgentState)
        builder.add_node("reason", self._reason)
        builder.add_node("act", self._act)
        builder.add_node("finalize", self._finalize)

        builder.set_entry_point("reason")
        builder.add_conditional_edges(
            "reason",
            self._route_after_reason,
            {
                "act": "act",
                "finalize": "finalize",
            },
        )
        builder.add_edge("act", "reason")
        builder.add_edge("finalize", END)

        if self.checkpointer:
            return builder.compile(checkpointer=self.checkpointer)
        return builder.compile()

    def _run_without_graph(self, state: AgentState) -> AgentState:
        local = state
        while True:
            local = self._reason(local)
            route = self._route_after_reason(local)
            if route == "finalize":
                return self._finalize(local)
            local = self._act(local)

    def _extract_json(self, content: str) -> dict[str, Any]:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return {
                "thought": "Failed to parse strict JSON, fallback to final answer.",
                "action": "finish",
                "action_input": {},
                "answer": content.strip(),
            }
        try:
            parsed = json.loads(match.group(0))
            parsed.setdefault("thought", "")
            parsed.setdefault("action", "finish")
            parsed.setdefault("action_input", {})
            parsed.setdefault("answer", "")
            return parsed
        except json.JSONDecodeError:
            return {
                "thought": "JSON decode error, fallback to final answer.",
                "action": "finish",
                "action_input": {},
                "answer": content.strip(),
            }

    def _reason(self, state: AgentState) -> AgentState:
        tool_specs = tool_registry.get_tool_specs()
        prompt = f"""
You are a ReAct agent. Decide one next step.

Available actions:
- search_docs
- get_course_schedule
- submit_repair_ticket
- generate_weekly_report
- finish

Tool specs: {json.dumps(tool_specs, ensure_ascii=False)}

Question: {state['question']}
User profile: {session_memory.get_or_create_profile(state['user_id'])}
Conversation history: {session_memory.get_recent_context(state['session_id'])}
Retrieved context: {state.get('context', '')}
Previous observations: {state.get('observations', [])}
Current step: {state.get('step', 0)}

Return ONLY JSON:
{{
  "thought": "reason briefly",
  "action": "one action from list",
  "action_input": {{"key": "value"}},
  "answer": "only fill when action=finish"
}}
""".strip()

        content = self.llm.invoke(prompt).content
        parsed = self._extract_json(content)

        state["thought"] = parsed["thought"]
        state["action"] = parsed["action"]
        state["action_input"] = parsed["action_input"]
        state["answer_candidate"] = parsed["answer"]
        return state

    def _route_after_reason(self, state: AgentState) -> str:
        if state.get("action") == "finish":
            return "finalize"
        if state.get("step", 0) >= settings.max_steps:
            return "finalize"
        return "act"

    def _act(self, state: AgentState) -> AgentState:
        action = state.get("action", "finish")
        action_input = state.get("action_input", {})
        observation: Any

        if action == "search_docs":
            query = action_input.get("query") or state["question"]
            hits = retriever_service.search(
                query=query,
                top_k=3,
                department=state.get("department"),
            )
            observation = [
                {
                    "content": hit.content[:200],
                    "metadata": hit.metadata,
                }
                for hit in hits
            ]
            if observation:
                joined = "\n".join(item["content"] for item in observation)
                state["context"] = f"{state.get('context', '')}\n{joined}".strip()
        elif any(spec["name"] == action for spec in tool_registry.get_tool_specs()):
            observation = tool_executor.execute(action, action_input)
        else:
            observation = {
                "error": f"Unknown action '{action}'",
                "fallback": "Please pick one supported action in next reasoning step.",
            }

        trace = state.setdefault("trace", [])
        trace.append(
            AgentStep(
                step=state.get("step", 0) + 1,
                thought=state.get("thought", ""),
                action=action,
                action_input=action_input,
                observation=observation,
            )
        )
        state.setdefault("observations", []).append(str(observation))
        state["step"] = state.get("step", 0) + 1
        return state

    def _finalize(self, state: AgentState) -> AgentState:
        if state.get("answer_candidate"):
            state["final_answer"] = state["answer_candidate"]
            return state

        summary_prompt = f"""
You are finalizing an answer for user question:
{state['question']}

Use these observations:
{state.get('observations', [])}

Use this context:
{state.get('context', '')}

Provide a concise Chinese answer.
"""
        state["final_answer"] = self.llm.invoke(summary_prompt).content
        return state

    def run(self, request: ChatRequest) -> ChatResponse:
        preview = retriever_service.search(
            query=request.message,
            top_k=3,
            department=request.department,
        )
        context = "\n".join(hit.content[:300] for hit in preview)

        invoke_payload: AgentState = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "question": request.message,
            "department": request.department,
            "step": 0,
            "trace": [],
            "observations": [],
            "context": context,
            "retrieved_preview": preview,
        }

        invoke_kwargs: dict[str, Any] = {}
        if self.checkpointer:
            invoke_kwargs["config"] = {"configurable": {"thread_id": request.session_id}}

        if self.graph is None:
            result = self._run_without_graph(invoke_payload)
        else:
            result = self.graph.invoke(invoke_payload, **invoke_kwargs)

        answer = result.get("final_answer", "当前未生成答案，请重试。")
        session_memory.append_session(request.session_id, "user", request.message)
        session_memory.append_session(request.session_id, "assistant", answer)

        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
            trace=result.get("trace", []),
            retrieval_preview=preview,
        )


react_agent_service = ReActAgentService()
