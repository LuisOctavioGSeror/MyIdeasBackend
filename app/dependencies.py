import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Header, HTTPException

from app.core.config import get_settings
from app import models
from app.models.users import User


# Load environment variables
load_dotenv()

# Database configuration
# Prefer DATABASE_URL (explicit). Otherwise, try to assemble from POSTGRES_* via Settings.
# Fallback to local SQLite so the app boots without envs.
s = get_settings()
DATABASE_URL = os.getenv("DATABASE_URL") or s.database_url or "sqlite:///./local.db"

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY") or s.secret_key or "dev-secret-key-change-me"
ALGORITHM = os.getenv("ALGORITHM") or s.algorithm or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = (
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    or str(s.access_token_expire_minutes)
    or "60"
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create database tables
#
# If you're running locally with SQLite and the schema changed (e.g. removed columns like `priority`),
# the existing `local.db` may be incompatible. In that case, we recreate it for a clean dev run.
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.replace("sqlite:///", "", 1)

    def _should_recreate_sqlite_db() -> bool:
        if db_path != "./local.db" or not os.path.exists(db_path):
            return False
        try:
            with engine.connect() as conn:
                cols = conn.exec_driver_sql("PRAGMA table_info(ideas);").fetchall()
            col_names = {row[1] for row in cols}  # row[1] = name
            # Old schema had `priority` column and no `image_url` column.
            return "priority" in col_names or "image_url" not in col_names
        except Exception:
            return False

    if _should_recreate_sqlite_db():
        try:
            os.remove(db_path)
        except OSError:
            pass

    models.base.Base.metadata.create_all(bind=engine)
else:
    models.base.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def require_api_key(x_api_key: str | None = Header(default=None)):
    s = get_settings()
    if s.api_key and x_api_key != s.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")