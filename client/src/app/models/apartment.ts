export interface Apartment {
  id: number;
  name: string;
  description: string;
  price_per_night: number;  
  capacity: number;
  bedrooms: number;
  bathrooms: number;
  image_url: string;  
  images?: string[];
  amenities: string[];
  address: string;
  city: string;
  rating?: number;
  created_at?: string;
  updated_at?: string;
}
