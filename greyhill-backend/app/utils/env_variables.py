from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv 
import os

class EnvVariables(BaseModel):    
    database_url: str
    admin_password: str
    homepage_url: str
    
    smtp_username: str
    smtp_password: str   
    admin_email: str
    
    #is_debug_mode: bool = False  # Príklad ďalšieho nastavenia


load_dotenv()  # Načíta premenné prostredia z .env súboru
EnvVariables = EnvVariables(    
    database_url=os.getenv("DATABASE_URL", "sqlite:///./greyhill.db"),  # Predvolená hodnota
    admin_password=os.getenv("ADMIN_PASSWORD", "default_admin_password"),
    homepage_url=os.getenv("HOMEPAGE_URL", "http://localhost:4200"),

    smtp_username=os.getenv("SMTP_USERNAME", "default_smtp_username"),
    smtp_password=os.getenv("SMTP_PASSWORD", "default_smtp_password"),
    admin_email=os.getenv("ADMIN_EMAIL", "default_admin_email"),    
    

    #is_debug_mode=os.getenv("IS_DEBUG_MODE", "false").lower() == "true"
)

def get_env_variables():
    return EnvVariables


