# seed_data.py

from app.database import SessionLocal, engine, Base
from app.models.apartment import Apartment
from app.models.user import User
from app.utils.auth import hash_password

# Vytvor tabuľky
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Vymaž staré dáta (voliteľné)
db.query(Apartment).delete()
db.commit()

# Vytvor testové apartmány
apartments = [
    {
        "name": "Luxusný apartmán centrum",
        "description": "Krásny priestranný apartmán v centre mesta s výhľadom na hory.",
        "price_per_night": 89.0,
        "capacity": 4,
        "bedrooms": 2,
        "bathrooms": 1,
        "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800",
        "amenities": ["WiFi", "TV", "Kuchyňa", "Parking", "Balkón"],
        "address": "Hlavná 123",
        "city": "Bratislava",
        "rating": 4.8
    },
    {
        "name": "Moderný loft s terasou",
        "description": "Štýlový loft s veľkou terasou, ideálny pre páry.",
        "price_per_night": 120.0,
        "capacity": 2,
        "bedrooms": 1,
        "bathrooms": 1,
        "image_url": "https://images.unsplash.com/photo-1502672260066-6bc36a69ce48?w=800",
        "amenities": ["WiFi", "TV", "Kuchyňa", "Terasa", "Klimatizácia"],
        "address": "Dunajská 45",
        "city": "Bratislava",
        "rating": 4.9
    },
    {
        "name": "Rodinný apartmán s garážou",
        "description": "Priestranný 3-izbový apartmán pre celú rodinu.",
        "price_per_night": 150.0,
        "capacity": 6,
        "bedrooms": 3,
        "bathrooms": 2,
        "image_url": "https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800",
        "amenities": ["WiFi", "TV", "Kuchyňa", "Parking", "Garáž", "Záhrada"],
        "address": "Lesná 78",
        "city": "Košice",
        "rating": 4.7
    }
]

for apt_data in apartments:
    apartment = Apartment(**apt_data)
    db.add(apartment)

db.commit()

print(f"✅ Vytvorených {len(apartments)} apartmánov!")

# Vytvor admin používateľa (ak neexistuje)
admin = db.query(User).filter(User.email == "admin@greyhill.sk").first()
if not admin:
    admin = User(
        email="admin@greyhill.sk",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("admin123"),
        is_admin=True
    )
    db.add(admin)
    db.commit()
    print("✅ Admin používateľ vytvorený! (admin@greyhill.sk / admin123)")

db.close()
print("✅ Databáza naplnená!")