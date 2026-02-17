from app.database import SessionLocal, engine, Base
from app.models.apartment import Apartment
from app.models.user import User
from app.models.booking import Booking
from app.utils.auth import hash_password


APARTMENTS_DATA = [
    {
        "name": "Luxusný apartmán centrum",
        "description": "Krásny priestranný apartmán v centre mesta.",
        "price_per_night": 100.0,
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
        #"image_url": "https://images.unsplash.com/photo-1502672260066-6bc36a69ce48?w=800",
        "image_url": "https://img.unitedclassifieds.sk/foto/Zml0LWluLzgwMHgyMDAwL2ZpbHRlcnM6cXVhbGl0eSg4MCk6Zm9ybWF0KHdlYnApL2p1bA==/e7ddx23rw_fss?st=l6jtclRnsXl6HYZQOwE9l48LY23SkLagngW_2ijesvc&ts=1769160045&e=0",
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


def create_tables():
    """Vytvor databázové tabuľky."""
    Base.metadata.create_all(bind=engine)

def create_apartments(db):
    """Vytvor testové apartmány."""
    existing_count = db.query(Apartment).count()
    if existing_count > 0:
        print(f"ℹ️  Už existuje {existing_count} apartmánov, preskočené vytváranie.")
        return
    
    for apt_data in APARTMENTS_DATA:
        apartment = Apartment(**apt_data)
        db.add(apartment)
    
    db.commit()
    print(f"✅ Vytvorených {len(APARTMENTS_DATA)} apartmánov!")


def create_admin_user(db):
    """Vytvor admin používateľa (ak neexistuje)."""
    admin = db.query(User).filter(User.email == "admin@greyhill.sk").first()
    if not admin:
        admin = User(
            email="admin@greyhill.sk",
            username="admin",
            full_name="Admin User",
            phone="+421911222333",
            hashed_password=hash_password("admin123"),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("✅ Admin používateľ vytvorený! (admin@greyhill.sk / admin123)")

def create_user(db):
    """Vytvor testového používateľa."""
    user = db.query(User).filter(User.email == "user@greyhill.sk").first()
    if not user:
        user = User(
            email="user@greyhill.sk",
            username="user",
            full_name="Test User",
            phone="+421940123456",
            hashed_password=hash_password("user123"),
            is_admin=False
        )
        db.add(user)
        db.commit()
        print("✅ Testový používateľ vytvorený! (user@greyhill.sk / user123)")
    return user


def create_bookings(db):
    """Vytvor testové rezervácie pre test používateľa."""
    from datetime import datetime, timedelta
    from app.models.booking import BookingStatus
    
    # Skontroluj či už existujú rezervácie
    existing_count = db.query(Booking).count()
    if existing_count > 0:
        print(f"ℹ️  Už existuje {existing_count} rezervácií, preskočené vytváranie.")
        return    

    # Získaj test používateľa
    user = db.query(User).filter(User.email == "user@greyhill.sk").first()
    if not user:
        print("❌ Test používateľ nenájdený!")
        return
    
    # Zisti dostupné apartmány
    apartments = db.query(Apartment).all()
    if len(apartments) < 2:
        print("❌ Nedostatok apartmánov na vytvorenie rezervácií!")
        return

    # Vytvor 2 rezervácie
    bookings = [
        Booking(
            apartment_id=apartments[0].id,
            guest_name="Test User",
            guest_email="user@greyhill.sk",
            guest_phone="+421940123456",
            check_in_date=datetime.now() + timedelta(days=5),
            check_out_date=datetime.now() + timedelta(days=7),
            number_of_adults=2,
            number_of_kids=1,
            total_price=(apartments[0].price_per_night * 2) - 5,
            status=BookingStatus.CONFIRMED,
            special_requests="Prosím, ranný check-in"
        ),
        Booking(
            apartment_id=apartments[1].id,
            guest_name="Test User",
            guest_email="user@greyhill.sk",
            guest_phone="+421940123456",
            check_in_date=datetime.now() + timedelta(days=10),
            check_out_date=datetime.now() + timedelta(days=15),
            number_of_adults=2,
            number_of_kids=0,
            total_price=apartments[1].price_per_night * 5,
            status=BookingStatus.PENDING,
            special_requests="Veľa vankúšov, prosím"
        )
    ]
    
    for booking in bookings:
        db.add(booking)
    
    db.commit()
    print(f"✅ Vytvorené 2 rezervácie pre používateľa user@greyhill.sk!")



def seed_database():
    """Inicializuj databázu s testovacími údajmi."""
    create_tables()
    
    db = SessionLocal()
    try:
        create_apartments(db)
        create_admin_user(db)
        create_user(db)
        create_bookings(db)
        print("✅ Databáza naplnená!")
    finally:
        db.close()

def clear_database():
    """Vymaž všetky dáta z databázy."""
    db = SessionLocal()
    try:
        db.query(Apartment).delete()
        db.query(User).filter(User.is_admin == False).delete()  # Nevymazávaj admin používateľov
        db.query(Booking).delete()
        db.commit()
        print("✅ Databáza vymazaná!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()