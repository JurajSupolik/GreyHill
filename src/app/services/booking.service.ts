// src/app/services/booking.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Booking } from '../models/booking';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class BookingService {
  private apiUrl = `${environment.apiUrl}/bookings`;

  constructor(private http: HttpClient) { }

  // Vytvor novú rezerváciu
  createBooking(bookingData: any): Observable<Booking> {
    return this.http.post<Booking>(this.apiUrl, bookingData);
  }

  // Získaj všetky rezervácie (len pre adminov)
  getAllBookings(): Observable<Booking[]> {
    return this.http.get<Booking[]>(this.apiUrl);
  }

  // Získaj rezervácie pre konkrétny apartmán
  getApartmentBookings(apartmentId: number): Observable<Booking[]> {
    return this.http.get<Booking[]>(`${this.apiUrl}/apartment/${apartmentId}`);
  }

  // Získaj jednu rezerváciu podľa ID
  getBookingById(bookingId: number): Observable<Booking> {
    return this.http.get<Booking>(`${this.apiUrl}/${bookingId}`);
  }

  // Zmeň status rezervácie (len pre adminov)
  updateBookingStatus(bookingId: number, status: string): Observable<Booking> {
    return this.http.put<Booking>(`${this.apiUrl}/${bookingId}/status`, { status });
  }

  // Zmaž rezerváciu (len pre adminov)
  deleteBooking(bookingId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${bookingId}`);
  }
}