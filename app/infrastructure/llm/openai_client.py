import json
from typing import Any, Iterable
from openai import OpenAI
from app.core.config import get_settings
from app.infrastructure.llm.base import LLMClient, LLMResult, ToolCall


class OpenAIClient(LLMClient):
    def __init__(self, model: str | None = None):
        s = get_settings()
        self.client = OpenAI(api_key=s.openai_api_key)
        self.model = model or s.openai_model
        self._tools_mapped: Any | None = None

    def map_tools(self, mcp_tools: list[Any]) -> Any:
        mapped = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or t.title or "",
                    "parameters": t.inputSchema
                    or {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            }
            for t in mcp_tools
        ]
        # guarda para chamadas subsequentes (followup/stream)
        self._tools_mapped = mapped
        return mapped

    def _to_result(self, resp) -> LLMResult:
        # tolerante a respostas inesperadas
        choices = getattr(resp, "choices", None) or []
        if not choices:
            return LLMResult(content="")
        m = choices[0].message
        tool_calls = []
        for c in (getattr(m, "tool_calls", None) or []):
            args = json.loads(c.function.arguments or "{}")
            tool_calls.append(ToolCall(id=c.id, name=c.function.name, arguments=args))
        return LLMResult(content=(m.content or ""), tool_calls=tool_calls)

    def first(self, messages: list[dict], tools_mapped: Any) -> LLMResult:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools_mapped,
                tool_choice="auto",
            )
            return self._to_result(resp)
        except Exception as e:
            # Propaga erro claro para o serviço
            raise RuntimeError(f"OpenAI error: {e}") from e

    def followup(self, messages: list[dict]) -> LLMResult:
        try:
            # reutiliza o mesmo conjunto de ferramentas da primeira chamada
            kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
            if self._tools_mapped:
                kwargs["tools"] = self._tools_mapped
                kwargs["tool_choice"] = "auto"

            resp = self.client.chat.completions.create(**kwargs)
            return self._to_result(resp)
        except Exception as e:
            raise RuntimeError(f"OpenAI error: {e}") from e

    def stream(self, messages: list[dict]) -> Iterable[str]:
        """
        Faz uma chamada streaming simples SEM novas tool_calls.
        Assume que qualquer uso de ferramentas já foi resolvido antes.
        """
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            choices = getattr(chunk, "choices", None) or []
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            if not delta:
                continue
            text = getattr(delta, "content", None) or ""
            if text:
                yield text
