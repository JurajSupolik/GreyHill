// src/app/models/booking.ts

export enum BookingStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  CANCELLED = 'CANCELLED',
  COMPLETED = 'COMPLETED'
}

export interface Booking {
  id: number;
  apartment_id: number;
  apartment?: {
    id: number;
    name: string;
    city: string;
    image_url: string;
    price_per_night?: number;
  };
  guest_name: string;
  guest_email: string;
  guest_phone: string;
  check_in_date: string;
  check_out_date: string;
  number_of_adults: number;
  number_of_kids: number;
  total_price: number;
  status: BookingStatus | string; // Môže byť enum alebo string
  special_requests?: string;
  created_at: string;
  updated_at?: string;
}

export interface BookingCreate {
  apartment_id: number;
  guest_name?: string;
  guest_email?: string;
  guest_phone: string;
  check_in_date: Date | string;
  check_out_date: Date | string;
  number_of_adults: number;
  number_of_kids: number;
  special_requests?: string;
}