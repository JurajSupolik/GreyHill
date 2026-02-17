from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ApartmentBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    price_per_night: float = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    bedrooms: int = Field(..., ge=0)
    bathrooms: int = Field(..., ge=0)
    image_url: Optional[str] = None
    images: Optional[List[str]] = []
    amenities: Optional[List[str]] = []
    address: Optional[str] = None
    city: Optional[str] = None
    rating: Optional[float] = Field(default=0.0, ge=0, le=5)

class ApartmentCreate(ApartmentBase):
    pass

class ApartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_night: Optional[float] = None
    capacity: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    address: Optional[str] = None
    city: Optional[str] = None
    rating: Optional[float] = None

class ApartmentResponse(ApartmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True