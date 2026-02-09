# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token, UserResponse
from app.utils.auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_active_user,
    get_current_admin_user
)
from app.utils.env_variables import EnvVariables, get_env_variables
import traceback
from seed_data import clear_database, seed_database

router = APIRouter()

# REGISTER - Registrácia nového používateľa
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        print("🔍 Začínam registráciu...")
        print(f"Email: {user_data.email}")
        print(f"Username: {user_data.username}")
        
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email už existuje"
            )
        
        print("✅ Email je OK")
        
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Používateľské meno už existuje"
            )
        
        print("✅ Username je OK")
        print("🔐 Hashujeme heslo...")
        
        try:
            hashed_pwd = hash_password(user_data.password)
            print(f"✅ Heslo zahashované")
        except Exception as e:
            print(f"❌ Chyba pri hashovaní: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chyba pri hashovaní hesla: {str(e)}"
            )
        
        print("💾 Vytváram používateľa...")
        
        try:
            new_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_pwd
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ Používateľ vytvorený! ID: {new_user.id}")
            
            return new_user
            
        except Exception as e:
            db.rollback()
            print(f"❌ Chyba pri vytváraní v DB: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chyba pri ukladaní do databázy: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Neočakávaná chyba: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Neočakávaná chyba: {str(e)}"
        )

# Spoločná funkcia pre prihlásenie
def _login_user(email: str, password: str, db: Session):
    try:
        print("🔍 Pokus o prihlásenie...")
        print(f"Email: {email}")
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("❌ Používateľ nenájdený")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nesprávny email alebo heslo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print("✅ Používateľ nájdený")
        print("🔐 Overujem heslo...")
        
        if not verify_password(password, user.hashed_password):
            print("❌ Nesprávne heslo")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nesprávny email alebo heslo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print("✅ Heslo OK")
        
        if not user.is_active:
            print("❌ Účet neaktívny")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Účet je neaktívny"
            )
        
        print("✅ Účet aktívny")
        print("🔑 Vytváram token...")
        
        access_token = create_access_token(data={"sub": user.email})
        
        print("✅ Token vytvorený")
        print(f"✅ Úspešné prihlásenie používateľa: {user.username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Neočakávaná chyba pri prihlásení: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chyba pri prihlásení: {str(e)}"
        )

# LOGIN - Prihlásenie používateľa (Form data pre Swagger OAuth2)
@router.post("/login", response_model=Token)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    return _login_user(username, password, db)

# LOGIN - Prihlásenie používateľa (JSON pre Angular)
@router.post("/login-json", response_model=Token)
def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    return _login_user(credentials.email, credentials.password, db)

# GET /me
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    print(f"✅ Požiadavka na /me od používateľa: {current_user.username}")
    return current_user

# LOGOUT
@router.post("/logout")
async def logout():
    print("✅ Odhlásenie")
    return {"message": "Úspešne odhlásený"}

# GET /users - Zoznam používateľov (len admin)
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    print(f"📋 Admin {current_user.username} žiada zoznam používateľov")
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users

# GET /admin/veraibles - Zobrazenie env premenných (len admin)
@router.get("/admin/variables")
async def get_env_variables_admin(
    #current_user: User = Depends(get_current_admin_user),
    current_user: User = Depends(get_current_active_user),
    env_vars: EnvVariables = Depends(get_env_variables)
):
    #print(f"📋 {current_user.username} žiada env premenné")    
    return env_vars