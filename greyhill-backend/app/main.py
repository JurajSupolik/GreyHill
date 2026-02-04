# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import apartments, auth, bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Greyhill API",
    description="Booking systém pre apartmány 1",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:4200"],
    allow_origins=["*"],  # Povoliť všetky originy (neodporúča sa v produkcii)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
