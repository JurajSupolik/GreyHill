from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.apartment import Apartment
from app.schemas.apartment import ApartmentCreate, ApartmentResponse, ApartmentUpdate

router = APIRouter()

@router.get("/", response_model=List[ApartmentResponse])
def get_apartments(
    skip: int = 0,
    limit: int = 100,
    city: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Apartment)
    
    if city:
        query = query.filter(Apartment.city.ilike(f"%{city}%"))
    
    apartments = query.offset(skip).limit(limit).all()
    return apartments

@router.get("/{apartment_id}", response_model=ApartmentResponse)
def get_apartment(apartment_id: int, db: Session = Depends(get_db)):
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment s ID {apartment_id} neexistuje"
        )
    
    return apartment

@router.post("/", response_model=ApartmentResponse, status_code=status.HTTP_201_CREATED)
def create_apartment(apartment: ApartmentCreate, db: Session = Depends(get_db)):
    db_apartment = Apartment(**apartment.model_dump())
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)
    return db_apartment

@router.put("/{apartment_id}", response_model=ApartmentResponse)
def update_apartment(
    apartment_id: int,
    apartment_update: ApartmentUpdate,
    db: Session = Depends(get_db)
):
    db_apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    
    if not db_apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment s ID {apartment_id} neexistuje"
        )
    
    update_data = apartment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_apartment, key, value)
    
    db.commit()
    db.refresh(db_apartment)
    return db_apartment

@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apartment(apartment_id: int, db: Session = Depends(get_db)):
    db_apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    
    if not db_apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment s ID {apartment_id} neexistuje"
        )
    
    db.delete(db_apartment)
    db.commit()
    return None