import os
from typing import Any, Final

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DB_URL: Final[str] = os.getenv("DB_URL") or ""
assert DB_URL, "DB_URL must be present in .env with a non-empty value."

engine: Engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal: sessionmaker[Session] = sessionmaker(  # pylint: disable=unsubscriptable-object
    autocommit=False, autoflush=False, bind=engine
)

Base: Any = declarative_base()
