# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.utils.env_variables import get_env_variables   
from dotenv import load_dotenv 
import os
#from app.settings import settings


# SQLite databáza
#SQLALCHEMY_DATABASE_URL = settings.database_url

# if settings.is_debug_mode:
#     print("Using database URL:", SQLALCHEMY_DATABASE_URL)

# Vytvor engine
load_dotenv()  # Načíta premenné prostredia z .env súboru

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if SQLALCHEMY_DATABASE_URL is None:
    print("DATABASE_URL not found. Using default SQLite URL.")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./greyhill.db"  # Default URL, ak nie je nastavené v .env

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

env_variables = get_env_variables()
if env_variables.is_debug_mode:
    print("database URL from .env:", SQLALCHEMY_DATABASE_URL)

# SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pre modely
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()