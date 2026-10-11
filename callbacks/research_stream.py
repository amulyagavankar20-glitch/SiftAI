import json
from typing import Any, Callable, Optional

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler


class ResearchStreamHandler(BaseCallbackHandler):
    """Print concise tool lifecycle events for interactive runs."""

    def __init__(
        self,
        verbose_json: bool = False,
        event_sink: Optional[Callable[[str, Any], None]] = None,
    ) -> None:
        self.verbose_json = verbose_json
        self.event_sink = event_sink

    def _emit(self, event_type: str, payload: Any) -> None:
        if self.event_sink:
            self.event_sink(event_type, payload)

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        self._emit("tool_started", {"tool": action.tool, "input": action.tool_input})
        print(f"\n[tool] {action.tool}")
        if self.verbose_json:
            print(json.dumps(action.tool_input, indent=2, default=str))

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        self._emit("tool_completed", {"output": str(output)[:800]})
        preview = str(output)
        print(f"[result] {preview[:600]}{'...' if len(preview) > 600 else ''}")

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        self._emit("tool_error", {"error": str(error)})
        print(f"[tool error] {error}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        self._emit("agent_finished", {"output": str(finish.return_values)[:2000]})
        print("[research complete]")
