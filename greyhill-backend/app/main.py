# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
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
path = os.getcwd()
print(f"Current working directory: {path}")
if os.name == "nt":  # NT kernel (Windows)
    print("Windows")
    os.makedirs("logs", exist_ok=True) 
    path = os.path.join(path, "logs")
elif os.name == "posix":  # POSIX kernel (Linux, macOS)
    print("Linux/MacOS")
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    path = os.path.join(path, "data/logs")

console_logger = LoggerFactory.create_console_logger()
file_logger = LoggerFactory.create_file_logger(file_path=os.path.join(path, "api_requests.log"))
print(f"Logging to: {os.path.join(path, 'api_requests.log')}")

app = FastAPI(
    title="Greyhill API",
    description="Booking systém pre apartmány Greyhill 1:06",
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
    allow_origins=["*"],  # Azure nastavia CORS policy, preto povolujeme všetky originy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# bug nesiel ssl zaciatok
# Confiuracia pre Azure
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]    
)
# Handle forwarded headers properly
from starlette.middleware.base import BaseHTTPMiddleware
class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):        
        if "x-forwarded-proto" in request.headers: # Azure passes these headers
            request.scope["scheme"] = request.headers["x-forwarded-proto"]
        response = await call_next(request)
        return response
app.add_middleware(ProxyHeadersMiddleware)
# bug nesiel ssl koniec

# Pridanie vlastného middleware pre logovanie
app.add_middleware(LoggingMiddleware,log_handler=custom_log_handler)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(apartments.router, prefix="/api/apartments", tags=["Apartments"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])

@app.get("/")
def root():
    return {
        "message": "Greyhill API",
        "version": "26.02.09",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
