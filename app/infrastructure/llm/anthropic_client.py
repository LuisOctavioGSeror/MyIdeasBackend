from typing import Any
from anthropic import Anthropic
from app.core.config import get_settings
from app.infrastructure.llm.base import LLMClient, LLMResult, ToolCall


class AnthropicClient(LLMClient):
    def __init__(self, model: str | None = None):
        s = get_settings()
        self.client = Anthropic(api_key=s.anthropic_api_key)
        self.model = model or s.anthropic_model


    def map_tools(self, mcp_tools: list[Any]) -> Any:
        tools = []
        for t in mcp_tools:
            tools.append({
            "name": t.name,
            "description": t.description or t.title or "",
            "input_schema": t.inputSchema or {"type": "object", "properties": {}, "additionalProperties": False},
            })
        return tools


    def first(self, messages: list[dict], tools_mapped: Any) -> LLMResult:
        msgs = [{"role": ("user" if m["role"] == "user" else "assistant"), "content": m["content"]} for m in messages]
        resp = self.client.messages.create(model=self.model, messages=msgs, tools=tools_mapped)
        uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        calls = [ToolCall(id=u.id, name=u.name, arguments=(u.input or {})) for u in uses]
        text = "".join([b.text for b in resp.content if getattr(b, "type", None) == "text"]) or None
        return LLMResult(content=text, tool_calls=calls)


    def followup(self, messages: list[dict]) -> LLMResult:
        msgs = [{"role": ("user" if m["role"] == "user" else "assistant"), "content": m["content"]} for m in messages]
        resp = self.client.messages.create(model=self.model, messages=msgs)
        text = "".join([b.text for b in resp.content if getattr(b, "type", None) == "text"]) or None
        return LLMResult(content=text, tool_calls=[])