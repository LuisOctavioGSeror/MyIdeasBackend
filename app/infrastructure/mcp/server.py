from fastapi import FastAPI
from fastapi_mcp import FastApiMCP


def mount_mcp(app: FastAPI) -> FastApiMCP:
    mcp = FastApiMCP(app)
    mcp.mount_http() # expõe /mcp
    return mcp