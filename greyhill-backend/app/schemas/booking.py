# app/schemas/booking.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ApartmentInfo(BaseModel):
    id: int
    name: str
    city: Optional[str] = None
    price_per_night: float
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    apartment_id: int
    guest_name: str = Field(..., min_length=2, max_length=200)
    guest_email: EmailStr
    guest_phone: Optional[str] = None
    check_in_date: datetime
    check_out_date: datetime
    number_of_adults: int = Field(..., gt=0)
    number_of_kids: int = Field(default=0)
    special_requests: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    guest_name: Optional[str] = None
    guest_phone: Optional[str] = None
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    number_of_adults: Optional[int] = None
    number_of_kids: Optional[int] = None
    special_requests: Optional[str] = None
    status: Optional[str] = None

class BookingResponse(BookingBase):
    id: int
    total_price: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    apartment: Optional[ApartmentInfo] = None  # ← PRIDANÉ

    class Config:
        from_attributes = True

class BookingStatusUpdate(BaseModel):
    status: str