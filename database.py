# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()  # will read .env if present

# You can set DB URL in .env as DATABASE_URL, else use this default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Shriram1!@localhost:3306/rag"
)

# SQLAlchemy engine & session factory
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
