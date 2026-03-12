from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Protocol


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResult:
    content: str | None = None
    tool_calls: List[ToolCall] = field(default_factory=list)  # <= nunca None


class LLMClient(Protocol):
    def map_tools(self, mcp_tools: list[Any]) -> Any: ...
    def first(self, messages: list[dict], tools_mapped: Any) -> LLMResult: ...
    def followup(self, messages: list[dict]) -> LLMResult: ...
    # Stream apenas para a resposta final (sem novas tool_calls)
    def stream(self, messages: list[dict]) -> Iterable[str]: ...

