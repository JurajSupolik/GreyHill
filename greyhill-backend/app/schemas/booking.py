# app/schemas/booking.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class BookingBase(BaseModel):
    apartment_id: int
    guest_name: str = Field(..., min_length=2, max_length=200)
    guest_email: EmailStr
    guest_phone: Optional[str] = None
    check_in_date: datetime
    check_out_date: datetime
    number_of_guests: int = Field(..., gt=0)
    special_requests: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    """Schema pre aktualizáciu rezervácie"""
    guest_name: Optional[str] = None
    guest_phone: Optional[str] = None
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    number_of_guests: Optional[int] = None
    special_requests: Optional[str] = None
    status: Optional[str] = None

class BookingResponse(BookingBase):
    id: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookingStatusUpdate(BaseModel):
    status: str