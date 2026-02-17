from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv 
import os

class EnvVariables(BaseModel):    
    database_url: str
    admin_password: str
    smtp_password: str   
    is_debug_mode: bool = False  


load_dotenv()  # Načíta premenné prostredia z .env súboru
EnvVariables = EnvVariables(    
    database_url=os.getenv("DATABASE_URL", "sqlite:///./greyhill.db"),  # Predvolená hodnota
    admin_password=os.getenv("ADMIN_PASSWORD", "default_admin_password"),
    smtp_password=os.getenv("SMTP_PASSWORD", "default_smtp_password"),
    is_debug_mode=os.getenv("IS_DEBUG_MODE", "false").lower() == "true"
)

def get_env_variables():
    return EnvVariables


