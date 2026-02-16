# greyhill-backend/app/routers/bookings.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db

# Configure logger for this module
logger = logging.getLogger(__name__)
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.models.apartment import Apartment
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate, BookingStatusUpdate
from app.utils.auth import get_current_user, get_current_user_optional
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
    logger.info(f"📋 Načítavanie rezervácií pre používateľa: {current_user.email}")
    bookings = db.query(Booking).filter(
        Booking.guest_email == current_user.email
    ).order_by(Booking.created_at.desc()).all()
    
    logger.info(f"✅ Nájdených {len(bookings)} rezervácií pre {current_user.email}")
    return bookings


@router.get("/", response_model=List[BookingResponse])
def get_all_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Získaj všetky rezervácie (admin) alebo len moje (user)"""
    if current_user.is_admin:
        logger.info(f"👑 Admin {current_user.email} načítava všetky rezervácie")
        bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    else:
        logger.info(f"👤 Používateľ {current_user.email} načítava svoje rezervácie")
        bookings = db.query(Booking).filter(
            Booking.guest_email == current_user.email
        ).order_by(Booking.created_at.desc()).all()
    
    logger.info(f"✅ Vrátených {len(bookings)} rezervácií")
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Získaj detail rezervácie"""
    logger.info(f"🔍 Používateľ {current_user.email} načítava rezerváciu #{booking_id}")
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        logger.warning(f"⚠️ Rezervácia #{booking_id} nenájdená")
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    # Kontrola oprávnení - len admin alebo vlastník rezervácie
    if not current_user.is_admin and booking.guest_email != current_user.email:
        logger.warning(f"🚫 Zamietnutý prístup k rezervácii #{booking_id} pre {current_user.email}")
        raise HTTPException(status_code=403, detail="Nemáte oprávnenie")
    
    logger.info(f"✅ Detail rezervácie #{booking_id} úspešne načítaný")
    return booking


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Vytvor novú rezerváciu"""
    # Log či je používateľ prihlásený
    if current_user:
        logger.info(f"✅ Používateľ je prihlásený: {current_user.email}")
        print(f"✅ Používateľ je prihlásený: {current_user.email}")
    else:
        logger.info(f"❌ Používateľ NIE JE prihlásený (anonymná rezervácia) - Email: {booking.guest_email or 'Neznámy email'}")
        print(f"❌ Používateľ NIE JE prihlásený (anonymná rezervace) - Email: {booking.guest_email or 'Neznámy email'}")
    
    # Skontroluj, či apartmán existuje
    apartment = db.query(Apartment).filter(Apartment.id == booking.apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartmán nenájdený")
    
    # Validácia dátumov
    if booking.check_out_date <= booking.check_in_date:
        raise HTTPException(
            status_code=400, 
            detail="Dátum odchodu musí byť po dátume príchodu"
        )
    
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
    #total_price = apartment.price_per_night * nights
    #total_price = (apartment.price_per_night * nights) * (booking.number_of_adults + booking.number_of_kids * 0.5)

    print(f"📅 Počet nocí: {nights}, dospelých: {booking.number_of_adults}, detí: {booking.number_of_kids}")

    base_price = apartment.price_per_night * 0.8; # 80 base price  
    print(f"💰 Základní cena (80%): {base_price} EUR")
    variable_price = apartment.price_per_night - base_price # 20% variabilní cena    
    print(f"💰 Variabilní cena (20%): {variable_price} EUR")

    adult_price = (variable_price / apartment.capacity * booking.number_of_adults)
    print(f"💰 Cena za dospelych: {adult_price} EUR")

    kids_price = (variable_price / apartment.capacity * booking.number_of_kids * 0.5) if booking.number_of_kids > 0 else 0    
    print(f"💰 Cena za děti: {kids_price} EUR")

    total_price = (base_price + adult_price + kids_price) * nights    
    logger.info(f"💰 Celková cena: {total_price} EUR")
    print(f"💰 Celková cena: {total_price} EUR")

    # Vytvor rezerváciu
    new_booking = Booking(
        apartment_id=booking.apartment_id,
        guest_name=booking.guest_name or (current_user.full_name if current_user else None),
        guest_email=booking.guest_email or (current_user.email if current_user else None),
        guest_phone=booking.guest_phone,
        check_in_date=booking.check_in_date,
        check_out_date=booking.check_out_date,
        number_of_adults=booking.number_of_adults,
        number_of_kids=booking.number_of_kids,
        total_price=total_price,
        status=BookingStatus.PENDING,
        special_requests=booking.special_requests
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    logger.info(f"✅ Rezervácia #{new_booking.id} úspešne vytvorená pre {new_booking.guest_email}")
    
    # 📧 POŠLI EMAILY
    try:
        # Email hosťovi
        booking_data = {
            'guest_name': new_booking.guest_name,
            'guest_email': new_booking.guest_email,
            'guest_phone': new_booking.guest_phone,
            'check_in_date': new_booking.check_in_date.isoformat(),
            'check_out_date': new_booking.check_out_date.isoformat(),
            'number_of_adults': new_booking.number_of_adults,
            'number_of_kids': new_booking.number_of_kids
        }
        
        send_booking_confirmation_email(
            booking_data=booking_data,
            apartment_name=apartment.name,
            total_price=total_price
        )
        logger.info(f"📧 Potvrdenie rezervácie odoslané na {new_booking.guest_email}")
        
        # Email adminovi
        send_admin_notification_email(
            booking_data=booking_data,
            apartment_name=apartment.name,
            total_price=total_price,
            booking_id=new_booking.id
        )
        logger.info(f"📧 Notifikácia adminovi odoslaná pre rezerváciu #{new_booking.id}")
    except Exception as e:
        print(f"⚠️ Email sa nepodarilo odoslať: {e}")
        logger.error(f"⚠️ Email sa nepodarilo odoslať: {e}")
        # Nezrušuj rezerváciu ak email zlyhá
    
    return new_booking


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zruš rezerváciu"""
    logger.info(f"🚫 Používateľ {current_user.email} ruší rezerváciu #{booking_id}")
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        logger.warning(f"⚠️ Rezervácia #{booking_id} nenájdená pri rušení")
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    # Kontrola oprávnení
    if not current_user.is_admin and booking.guest_email != current_user.email:
        logger.warning(f"🚫 Zamietnuté zrušenie rezervácie #{booking_id} pre {current_user.email}")
        raise HTTPException(status_code=403, detail="Nemáte oprávnenie zrušiť túto rezerváciu")
    
    # Skontroluj, či rezervácia už nie je zrušená
    if booking.status == BookingStatus.CANCELLED:
        logger.info(f"⚠️ Rezervácia #{booking_id} už bola zrušená")
        raise HTTPException(status_code=400, detail="Rezervácia už bola zrušená")
    
    # Zruš rezerváciu
    old_status = booking.status
    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    
    logger.info(f"✅ Rezervácia #{booking_id} úspešne zrušená (stavy: {old_status.value} → {BookingStatus.CANCELLED.value})")
    
    # 📧 POŠLI EMAIL O ZRUŠENÍ
    if old_status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        try:
            apartment = db.query(Apartment).filter(Apartment.id == booking.apartment_id).first()
            booking_data = {
                'guest_name': booking.guest_name,
                'guest_email': booking.guest_email,
                'check_in_date': booking.check_in_date.isoformat(),
                'check_out_date': booking.check_out_date.isoformat(),
                'number_of_adults': booking.number_of_adults,
                'number_of_kids': booking.number_of_kids,
                'total_price': booking.total_price
            }
            
            send_booking_cancelled_email(
                booking=booking_data,
                apartment_name=apartment.name if apartment else "Neznámy apartmán"
            )
            logger.info(f"📧 Email o zrušení odoslaný na {booking.guest_email}")
        except Exception as e:
            print(f"⚠️ Email zrušenia sa nepodarilo odoslať: {e}")
            logger.error(f"⚠️ Email zrušenia sa nepodarilo odoslať: {e}")
    
    return booking


@router.put("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualizuj stav rezervácie (admin only)"""
    logger.info(f"🔄 Admin {current_user.email} mení stav rezervácie #{booking_id} na {status_update.status}")
    if not current_user.is_admin:
        logger.warning(f"🚫 Nepovolený pokus o zmenu stavu rezervácie #{booking_id} od {current_user.email}")
        raise HTTPException(status_code=403, detail="Len admin môže meniť stav rezervácie")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        logger.warning(f"⚠️ Rezervácia #{booking_id} nenájdená pri zmene stavu")
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    # Validuj status
    try:
        new_status = BookingStatus[status_update.status.upper()]
        old_status = booking.status
        booking.status = new_status
    except KeyError:
        logger.error(f"❌ Neplatný status: {status_update.status}")
        raise HTTPException(status_code=400, detail="Neplatný status")
    
    db.commit()
    db.refresh(booking)
    
    logger.info(f"✅ Stav rezervácie #{booking_id} zmenený: {old_status.value} → {new_status.value}")
    
    # 📧 POŠLI EMAIL PRI ZMENE STATUSU
    try:
        apartment = db.query(Apartment).filter(Apartment.id == booking.apartment_id).first()
        booking_data = {
            'guest_name': booking.guest_name,
            'guest_email': booking.guest_email,
            'check_in_date': booking.check_in_date.isoformat(),
            'check_out_date': booking.check_out_date.isoformat(),
            'number_of_adults': booking.number_of_adults,
            'number_of_kids': booking.number_of_kids,
            'total_price': booking.total_price
        }
        
        # Email pri potvrdení
        if old_status == BookingStatus.PENDING and new_status == BookingStatus.CONFIRMED:
            send_booking_confirmed_email(
                booking=booking_data,
                apartment_name=apartment.name if apartment else "Neznámy apartmán"
            )
            logger.info(f"📧 Email potvrdenia odoslaný na {booking.guest_email}")
        
        # Email pri zrušení
        elif new_status == BookingStatus.CANCELLED and old_status != BookingStatus.CANCELLED:
            send_booking_cancelled_email(
                booking=booking_data,
                apartment_name=apartment.name if apartment else "Neznámy apartmán"
            )
            logger.info(f"📧 Email zrušenia odoslaný na {booking.guest_email}")
    except Exception as e:
        print(f"⚠️ Email sa nepodarilo odoslať: {e}")
        logger.error(f"⚠️ Email sa nepodarilo odoslať: {e}")
    
    return booking


@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vymaž rezerváciu (len admin)"""
    logger.info(f"🗑️ Admin {current_user.email} maže rezerváciu #{booking_id}")
    if not current_user.is_admin:
        logger.warning(f"🚫 Nepovolený pokus o zmazanie rezervácie #{booking_id} od {current_user.email}")
        raise HTTPException(status_code=403, detail="Len admin môže mazať rezervácie")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        logger.warning(f"⚠️ Rezervácia #{booking_id} nenájdená pri mazaní")
        raise HTTPException(status_code=404, detail="Rezervácia nenájdená")
    
    guest_email = booking.guest_email
    db.delete(booking)
    db.commit()
    
    logger.info(f"✅ Rezervácia #{booking_id} ({guest_email}) úspešne vymazaná")
    return {"message": "Rezervácia vymazaná"}


@router.get("/availability/{apartment_id}")
def get_availability(
    apartment_id: int,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Získaj dostupnosť apartmánu"""
    logger.info(f"📅 Kontrola dostupnosti apartmánu #{apartment_id}")
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not apartment:
        logger.warning(f"⚠️ Apartmán #{apartment_id} nenájdený")
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
    
    logger.info(f"✅ Apartmán #{apartment_id}: {len(booked_dates)} aktívnych rezervácií")
    return {
        "apartment_id": apartment_id,
        "booked_dates": booked_dates
    }