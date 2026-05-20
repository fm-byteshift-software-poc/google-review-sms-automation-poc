"""
Database connection and session management.
Part of the repository/infrastructure layer.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os

# Database path configuration
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'app.db'}")

# SQLAlchemy engine configuration
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

Base = declarative_base()


def get_db():
    """
    Dependency generator for FastAPI routes.
    Yields a database session and ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables. Call this once at application startup.
    """
    from models import Submission, Feedback, ReviewReply  # noqa: F401
    Base.metadata.create_all(bind=engine)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Configure SQLite pragmas for better performance and foreign key support.
    """
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()