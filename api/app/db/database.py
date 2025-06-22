"""SqlAlchemy database session"""

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("postgresql://postgres:postgres@db/septa_walking_app")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BASE = declarative_base()


def request_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
