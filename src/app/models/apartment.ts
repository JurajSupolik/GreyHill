// src/app/models/apartment.ts

export interface Apartment {
  id: number;
  name: string;
  description: string;
  pricePerNight: number;
  capacity: number;
  bedrooms: number;
  bathrooms: number;
  imageUrl: string;
  images?: string[];
  amenities: string[];
  address: string;
  city: string;
  rating?: number;
}
