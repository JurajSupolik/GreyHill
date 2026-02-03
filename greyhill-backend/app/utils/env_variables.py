from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv 
import os

class EnvVariables(BaseModel):
    secret_key: str
    database_url: str
    is_debug_mode: bool = False  # Príklad ďalšieho nastavenia


load_dotenv()  # Načíta premenné prostredia z .env súboru
EnvVariables = EnvVariables(
    secret_key=os.getenv("SECRET_KEY", "default_secret_key"),
    database_url=os.getenv("DATABASE_URL", "sqlite:///./greyhill.db"),  # Predvolená hodnota
    is_debug_mode=os.getenv("IS_DEBUG_MODE", "false").lower() == "true"
)

def get_env_variables():
    return EnvVariables


