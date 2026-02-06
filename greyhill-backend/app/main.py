# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import apartments, auth, bookings
from seed_data import seed_database

from app.middlewares.logging import LoggingMiddleware,RequestLogData
from app.core.logging import LoggerFactory
import os

# Vytvorenie všetkých databázových tabuliek
#Base.metadata.create_all(bind=engine)
seed_database()

# Inicializácia loggerov
os.makedirs("logs", exist_ok=True) 
console_logger = LoggerFactory.create_console_logger()
file_logger = LoggerFactory.create_file_logger(file_path="logs/api_requests.log")

app = FastAPI(
    title="Greyhill API",
    description="Booking systém pre apartmány Greyhill 2",
    version="1.0.0"
)

def custom_log_handler(log_data: RequestLogData):
    log_message = (
        f"{log_data.method} {log_data.path} - "
        f"ID: {log_data.request_id} - "
        f"Status: {log_data.status_code} - "
        f"IP: {log_data.client_ip} - "
        f"UA: {log_data.user_agent} - "
        f"Duration: {log_data.duration_ms}ms"
    )
    console_logger.info(log_message)
    file_logger.info(log_message)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200", 
        "http://greyhill.azurewebsites.net",
        "https://greyhill.azurewebsites.net", 
        "https://greyhill-api.azurewebsites.net"],
    #allow_origins=["*"],  # Povoliť všetky originy (neodporúča sa v produkcii)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pridanie vlastného middleware pre logovanie
app.add_middleware(LoggingMiddleware,log_handler=custom_log_handler)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(apartments.router, prefix="/api/apartments", tags=["Apartments"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])

@app.get("/")
def root():
    return {
        "message": "Greyhill API",
        "version": "26.02.04",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
