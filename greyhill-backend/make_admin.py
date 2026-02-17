from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()

# Nájdi používateľa podľa emailu
email = "jurajsupolik@gmail.com"
user = db.query(User).filter(User.email == email).first()

if user:
    # Urob ho adminom
    user.is_admin = True
    db.commit()
    print(f"✅ Používateľ {user.username} ({user.email}) je teraz ADMIN! 👑")
else:
    print(f"❌ Používateľ s emailom {email} neexistuje!")

db.close()