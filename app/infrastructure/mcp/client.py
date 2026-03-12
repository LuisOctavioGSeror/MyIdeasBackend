from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Dict, Any
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


@asynccontextmanager
async def mcp_session(mcp_url: str, token: Optional[str] = None) -> AsyncIterator[ClientSession]:
    """
    Abre uma sessão MCP HTTP apontando para o próprio FastAPI.
    Se receber um token JWT, encaminha como Authorization Bearer
    para que os tools MCP consigam chamar rotas protegidas (/ideas, etc.).
    """
    headers: Dict[str, Any] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with streamablehttp_client(mcp_url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session