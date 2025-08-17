"""SqlAlchemy database session"""
import os
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

engine = create_engine(os.getenv('DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BASE = declarative_base()


def request_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
