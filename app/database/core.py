"""
Database core utilities and dependency provider.

This module configures the SQL engine, session factory and exposes a
`get_db` dependency suitable for FastAPI endpoints. It also defines the
Declarative `Base` used by application ORM models.
"""
from typing import Annotated

from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlmodel import create_engine

from app.config import settings

from fastapi import Depends


if settings.DEBUG:
    DATABASE_URL = settings.DATABASE_URL
else:
    DATABASE_URL = settings.PROD_DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True) # echo must be False in production

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase): # this is the base class for all our models ensuring that python classed are mapped to database tables
    """Base class for ORM models used by SQLModel/SQLAlchemy."""
    pass

metadata = Base.metadata


def get_db():
    """
    FastAPI dependency that yields a database session and ensures it is
    closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]