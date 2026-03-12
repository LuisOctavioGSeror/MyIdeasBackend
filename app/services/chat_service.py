# app/services/chat_service.py
import os, re, json
from typing import Any, AsyncIterator, Iterable
from app.infrastructure.llm.base import LLMClient
from app.infrastructure.mcp.client import mcp_session

EXCLUDE_PATTERNS = os.getenv("MCP_EXCLUDE_TOOLS", r"^(chat_|auth_|health_)").split(",")

def _excluded(name: str) -> bool:
    return any(re.search(p.strip(), name) for p in EXCLUDE_PATTERNS if p.strip())

async def _extract_text(result: Any) -> str:
    try:
        from mcp import types as mcpt
        blk = result.content[0] if getattr(result, "content", None) else None
        if isinstance(blk, mcpt.TextContent):
            return blk.text
    except Exception:
        pass
    return json.dumps(getattr(result, "structuredContent", None) or {}, ensure_ascii=False)

class ChatService:
    def __init__(self, llm: LLMClient, mcp_url: str):
        self.llm = llm
        self.mcp_url = mcp_url

    async def run(self, messages: list[dict], token: str | None = None) -> str:
        async with mcp_session(self.mcp_url, token=token) as session:
            listed = await session.list_tools()
            mcp_tools = [t for t in listed.tools if not _excluded(t.name)]
            mapped = self.llm.map_tools(mcp_tools)

            msgs = messages.copy()
            base_len = len(msgs)
            while True:
                result = (
                    self.llm.first(msgs, mapped)
                    if len(msgs) == base_len
                    else self.llm.followup(msgs)
                )
                if result.tool_calls:
                    for call in result.tool_calls:
                        tool_res = await session.call_tool(
                            call.name, arguments=call.arguments
                        )
                        msgs.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "name": call.name,
                                "content": await _extract_text(tool_res),
                            }
                        )
                    continue
                return result.content or ""

    async def stream(
        self, messages: list[dict], token: str | None = None
    ) -> AsyncIterator[str]:
        """
        Versão streaming: resolve tool calls com chamadas normais
        e faz streaming apenas da resposta final do modelo.
        """
        async with mcp_session(self.mcp_url, token=token) as session:
            listed = await session.list_tools()
            mcp_tools = [t for t in listed.tools if not _excluded(t.name)]
            mapped = self.llm.map_tools(mcp_tools)

            msgs = messages.copy()
            base_len = len(msgs)
            while True:
                result = (
                    self.llm.first(msgs, mapped)
                    if len(msgs) == base_len
                    else self.llm.followup(msgs)
                )
                if result.tool_calls:
                    for call in result.tool_calls:
                        tool_res = await session.call_tool(
                            call.name, arguments=call.arguments
                        )
                        msgs.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "name": call.name,
                                "content": await _extract_text(tool_res),
                            }
                        )
                    continue

                # Sem novas tool_calls: fazemos uma última chamada em modo streaming
                for chunk in self.llm.stream(msgs):
                    if chunk:
                        yield chunk
                return
