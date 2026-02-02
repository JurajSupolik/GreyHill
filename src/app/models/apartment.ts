// src/app/models/apartment.ts

export interface Apartment {
  id: number;
  name: string;
  description: string;
  price_per_night: number;  // ← zmenené z pricePerNight
  capacity: number;
  bedrooms: number;
  bathrooms: number;
  image_url: string;  // ← zmenené z imageUrl
  images?: string[];
  amenities: string[];
  address: string;
  city: string;
  rating?: number;
  created_at?: string;
  updated_at?: string;
}
