from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.utils.env_variables import get_env_variables   
from dotenv import load_dotenv 
import os


# Vytvor engine
load_dotenv()  # Načíta premenné prostredia z .env súboru

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if SQLALCHEMY_DATABASE_URL is None:
    print("DATABASE_URL not found. Using default SQLite URL.")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./greyhill.db"  

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

env_variables = get_env_variables()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()