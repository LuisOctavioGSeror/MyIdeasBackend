from fastapi import FastAPI
from .routers import (auth, users, chat, ideas, uploads)
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.infrastructure.mcp.server import mount_mcp

s = get_settings()
app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(ideas.router)
app.include_router(uploads.router)

mount_mcp(app)

@app.get("/")
def root():
    return {"message": "MyTicketFLow API. All Rights Reserved."}