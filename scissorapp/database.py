from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .instance.config import get_settings


engine = create_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
