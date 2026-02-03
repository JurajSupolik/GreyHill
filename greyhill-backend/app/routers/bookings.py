# app/routers/bookings.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.apartment import Apartment
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse, BookingStatusUpdate
from app.utils.auth import get_current_active_user, get_current_admin_user
from app.utils.email import (
    send_booking_confirmation_email, 
    send_admin_notification_email,
    send_booking_confirmed_email,
    send_booking_cancelled_email
)

router = APIRouter()

# POST - Vytvor novú rezerváciu
@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    print(f"📅 Nova rezervacia pre apartman ID: {booking_data.apartment_id}")
    
    # Skontroluj, či apartmán existuje
    apartment = db.query(Apartment).filter(Apartment.id == booking_data.apartment_id).first()
    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Apartmán neexistuje"
        )
    
    # Validácia dátumov
    if booking_data.check_in_date >= booking_data.check_out_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dátum odchodu musí byť po dátume príchodu"
        )
    
    # Porovnaj s UTC datetime
    now_utc = datetime.now(timezone.utc)
    if booking_data.check_in_date < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dátum príchodu nemôže byť v minulosti"
        )
    
    # Skontroluj dostupnosť (či sa termíny neprekrývajú s existujúcimi rezerváciami)
    overlapping = db.query(Booking).filter(
        Booking.apartment_id == booking_data.apartment_id,
        Booking.status != BookingStatus.CANCELLED,
        Booking.check_in_date < booking_data.check_out_date,
        Booking.check_out_date > booking_data.check_in_date
    ).first()
    
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apartmán nie je dostupný v požadovanom termíne"
        )
    
    # Vypočítaj celkovú cenu
    days = (booking_data.check_out_date - booking_data.check_in_date).days
    total_price = days * apartment.price_per_night
    
    print(f"💰 Celkova cena: {days} dni × {apartment.price_per_night}€ = {total_price}€")
    
    # Vytvor rezerváciu
    new_booking = Booking(
        apartment_id=booking_data.apartment_id,
        guest_name=booking_data.guest_name,
        guest_email=booking_data.guest_email,
        guest_phone=booking_data.guest_phone,
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
        number_of_guests=booking_data.number_of_guests,
        total_price=total_price,
        special_requests=booking_data.special_requests,
        status=BookingStatus.PENDING
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    print(f"✅ Rezervacia vytvorena! ID: {new_booking.id}")
    
    # 📧 ODOŠLI EMAILY
    booking_dict = {
        'guest_name': booking_data.guest_name,
        'guest_email': booking_data.guest_email,
        'guest_phone': booking_data.guest_phone,
        'check_in_date': booking_data.check_in_date.isoformat(),
        'check_out_date': booking_data.check_out_date.isoformat(),
        'number_of_guests': booking_data.number_of_guests
    }
    
    # Email hosťovi
    send_booking_confirmation_email(booking_dict, apartment.name, total_price)
    
    # Email adminovi
    send_admin_notification_email(booking_dict, apartment.name, total_price, new_booking.id)
    
    return new_booking

# GET - Všetky rezervácie (len admin)
@router.get("/", response_model=List[BookingResponse])
async def get_all_bookings(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    return bookings

# GET - Rezervácie pre konkrétny apartmán
@router.get("/apartment/{apartment_id}", response_model=List[BookingResponse])
def get_apartment_bookings(apartment_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(
        Booking.apartment_id == apartment_id
    ).order_by(Booking.check_in_date).all()
    return bookings

# GET - Jedna rezervácia podľa ID
@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezervácia neexistuje"
        )
    return booking

# GET - Rezervácie podla emailu hosťa
@router.get("/guest/{guest_email}", response_model=List[BookingResponse])   
def get_bookings_by_guest_email(guest_email: str, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(
        Booking.guest_email == guest_email
    ).order_by(Booking.created_at.desc()).all()
    
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenalezen žádná rezervace pro tento email"
        )
    
    return bookings

# PUT - Zmeň status rezervácie (len admin)
@router.put("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezervácia neexistuje"
        )
    
    # Ulož starý status
    old_status = booking.status
    new_status = BookingStatus(status_update.status)
    
    # Zmeň status
    booking.status = new_status
    db.commit()
    db.refresh(booking)
    
    print(f"✅ Status rezervacie {booking_id} zmeneny z {old_status} na {new_status}")
    
    # 📧 ODOŠLI EMAIL AK SA STATUS ZMENIL NA CONFIRMED ALEBO CANCELLED
    apartment = db.query(Apartment).filter(Apartment.id == booking.apartment_id).first()
    
    if apartment:
        booking_dict = {
            'guest_name': booking.guest_name,
            'guest_email': booking.guest_email,
            'guest_phone': booking.guest_phone,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'number_of_guests': booking.number_of_guests,
            'total_price': booking.total_price
        }
        
        if new_status == BookingStatus.CONFIRMED and old_status != BookingStatus.CONFIRMED:
            send_booking_confirmed_email(booking_dict, apartment.name)
        
        elif new_status == BookingStatus.CANCELLED and old_status != BookingStatus.CANCELLED:
            send_booking_cancelled_email(booking_dict, apartment.name)
    
    return booking
# GET - Dostupnosť apartmánu (kalendár)
@router.get("/availability/{apartment_id}")
def get_apartment_availability(
    apartment_id: int,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """
    Vráti zoznam obsadených dátumov pre kalendár.
    Query params:
    - start_date: YYYY-MM-DD (voliteľné, default: dnes)
    - end_date: YYYY-MM-DD (voliteľné, default: +3 mesiace)
    """
    
    # Ak nie sú zadané dátumy, použij default
    if not start_date:
        start = datetime.now(timezone.utc)
    else:
        start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    
    if not end_date:
        end = start + timedelta(days=90)  # 3 mesiace dopredu
    else:
        end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
    
    # Získaj všetky aktívne rezervácie v tomto období
    bookings = db.query(Booking).filter(
        Booking.apartment_id == apartment_id,
        Booking.status != BookingStatus.CANCELLED,
        Booking.check_in_date <= end,
        Booking.check_out_date >= start
    ).all()
    
    # Vytvor zoznam obsadených dátumov
    occupied_dates = []
    for booking in bookings:
        current_date = booking.check_in_date.date()
        end_date_obj = booking.check_out_date.date()
        
        while current_date < end_date_obj:
            occupied_dates.append(current_date.isoformat())
            current_date += timedelta(days=1)
    
    return {
        "apartment_id": apartment_id,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "occupied_dates": occupied_dates,
        "bookings_count": len(bookings)
    }
# DELETE - Zmaž rezerváciu (len admin)
@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rezervácia neexistuje"
        )
    
    db.delete(booking)
    db.commit()
    
    print(f"🗑️ Rezervacia {booking_id} vymazana")
    
    return None