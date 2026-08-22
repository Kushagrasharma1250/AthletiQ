import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing from .env"
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)