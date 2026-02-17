from app.database import Base, engine
from app.models.booking import Booking
from app.models.apartment import Apartment
from app.models.user import User

# Vytvor všetky tabuľky
Base.metadata.create_all(bind=engine)

print("✅ Databázové tabuľky vytvorené (vrátane bookings)!")