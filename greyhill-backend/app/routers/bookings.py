# greyhill-backend/app/routers/bookings.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.models.apartment import Apartment
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate, BookingStatusUpdate
from app.utils.auth import get_current_user
from app.utils.email import (
    send_booking_confirmation_email,
    send_admin_notification_email,
    send_booking_confirmed_email,
    send_booking_cancelled_email
)

router = APIRouter()


@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Získaj všetky rezervácie aktuálneho užívateľa"""
    bookings = db.query(Booking).filter(
        Booking.guest_email == current_user.email
    ).order_by(Booking.created_at.desc()).all()
    
    return bookings


@router.get("/", response_model=List[BookingResponse])
def get_all_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Získaj všetky rezervácie (admin) alebo len moje (user)"""
    if current_user.is_admin:
        bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    else:
        bookings = db.query(Booking).filter(
            Booking.guest_email == current_user.email
        ).order_by(Booking.created_at.desc()).all()
    
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Získaj detail rezervácie"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    # Kontrola oprávnení - len admin alebo vlastník rezervácie
    if not current_user.is_admin and booking.guest_email != current_user.email:
        raise HTTPException(status_code=403, detail="Nemáte oprávnenie")
    
    return booking


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vytvor novú rezerváciu"""
    # Skontroluj, či apartmán existuje
    apartment = db.query(Apartment).filter(Apartment.id == booking.apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartmán nenájdený")
    
    # Skontroluj dostupnosť
    existing_bookings = db.query(Booking).filter(
        Booking.apartment_id == booking.apartment_id,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        Booking.check_out_date > booking.check_in_date,
        Booking.check_in_date < booking.check_out_date
    ).first()
    
    if existing_bookings:
        raise HTTPException(
            status_code=400, 
            detail="Apartmán nie je dostupný v tomto termíne"
        )
    
    # Vypočítaj celkovú cenu
    nights = (booking.check_out_date - booking.check_in_date).days
    total_price = apartment.price_per_night * nights
    
    # Vytvor rezerváciu
    new_booking = Booking(
        apartment_id=booking.apartment_id,
        guest_name=booking.guest_name or current_user.full_name,
        guest_email=booking.guest_email or current_user.email,
        guest_phone=booking.guest_phone,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        number_of_guests=booking.number_of_guests,
        total_price=total_price,
        status=BookingStatus.PENDING,
        special_requests=booking.special_requests
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    # 📧 POŠLI EMAILY
    try:
        # Email hosťovi
        booking_data = {
            'guest_name': new_booking.guest_name,
            'guest_email': new_booking.guest_email,
            'guest_phone': new_booking.guest_phone,
            'check_in_date': new_booking.check_in_date.isoformat(),
            'check_out_date': new_booking.check_out_date.isoformat(),
            'number_of_guests': new_booking.number_of_guests
        }
        
        send_booking_confirmation_email(
            booking_data=booking_data,
            apartment_name=apartment.name,
            total_price=total_price
        )
        
        # Email adminovi
        send_admin_notification_email(
            booking_data=booking_data,
            apartment_name=apartment.name,
            total_price=total_price,
            booking_id=new_booking.id
        )
    except Exception as e:
        print(f"⚠️ Email sa nepodarilo odoslať: {e}")
        # Nezrušuj rezerváciu ak email zlyhá
    
    return new_booking


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zruš rezerváciu"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    # Kontrola oprávnení
    if not current_user.is_admin and booking.guest_email != current_user.email:
        raise HTTPException(status_code=403, detail="Nemáte oprávnenie zrušiť túto rezerváciu")
    
    # Skontroluj, či rezervácia už nie je zrušená
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Rezervácia už bola zrušená")
    
    # Zruš rezerváciu
    old_status = booking.status
    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    
    # 📧 POŠLI EMAIL O ZRUŠENÍ
    if old_status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        try:
            apartment = db.query(Apartment).filter(Apartment.id == booking.apartment_id).first()
            booking_data = {
                'guest_name': booking.guest_name,
                'guest_email': booking.guest_email,
                'check_in_date': booking.check_in_date.isoformat(),
                'check_out_date': booking.check_out_date.isoformat(),
                'number_of_guests': booking.number_of_guests,
                'total_price': booking.total_price
            }
            
            send_booking_cancelled_email(
                booking=booking_data,
                apartment_name=apartment.name if apartment else "Neznámy apartmán"
            )
        except Exception as e:
            print(f"⚠️ Email zrušenia sa nepodarilo odoslať: {e}")
    
    return booking


@router.put("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualizuj stav rezervácie (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Len admin môže meniť stav rezervácie")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    # Validuj status
    try:
        new_status = BookingStatus[status_update.status.upper()]
        old_status = booking.status
        booking.status = new_status
    except KeyError:
        raise HTTPException(status_code=400, detail="Neplatný status")
    
    db.commit()
    db.refresh(booking)
    
    # 📧 POŠLI EMAIL PRI ZMENE STATUSU
    try:
        apartment = db.query(Apartment).filter(Apartment.id == booking.apartment_id).first()
        booking_data = {
            'guest_name': booking.guest_name,
            'guest_email': booking.guest_email,
            'check_in_date': booking.check_in_date.isoformat(),
            'check_out_date': booking.check_out_date.isoformat(),
            'number_of_guests': booking.number_of_guests,
            'total_price': booking.total_price
        }
        
        # Email pri potvrdení
        if old_status == BookingStatus.PENDING and new_status == BookingStatus.CONFIRMED:
            send_booking_confirmed_email(
                booking=booking_data,
                apartment_name=apartment.name if apartment else "Neznámy apartmán"
            )
        
        # Email pri zrušení
        elif new_status == BookingStatus.CANCELLED and old_status != BookingStatus.CANCELLED:
            send_booking_cancelled_email(
                booking=booking_data,
                apartment_name=apartment.name if apartment else "Neznámy apartmán"
            )
    except Exception as e:
        print(f"⚠️ Email sa nepodarilo odoslať: {e}")
    
    return booking


@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vymaž rezerváciu (len admin)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Len admin môže mazať rezervácie")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    db.delete(booking)
    db.commit()
    
    return {"message": "Rezervácia vymazaná"}


@router.get("/availability/{apartment_id}")
def get_availability(
    apartment_id: int,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Získaj dostupnosť apartmánu"""
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartmán nenájdený")
    
    # Získaj všetky potvrdené rezervácie
    bookings = db.query(Booking).filter(
        Booking.apartment_id == apartment_id,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
    ).all()
    
    booked_dates = []
    for booking in bookings:
        booked_dates.append({
            "check_in": booking.check_in_date.isoformat(),
            "check_out": booking.check_out_date.isoformat(),
            "status": booking.status.value
        })
    
    return {
        "apartment_id": apartment_id,
        "booked_dates": booked_dates
    }