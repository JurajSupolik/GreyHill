// src/app/services/booking.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Booking } from '../models/booking';

@Injectable({
  providedIn: 'root'
})
export class BookingService {
  private apiUrl = `${environment.apiUrl}/bookings`;

  constructor(private http: HttpClient) { }

  // Získaj moje rezervácie
  getMyBookings(): Observable<Booking[]> {
    return this.http.get<Booking[]>(`${this.apiUrl}/my-bookings`);
  }

  // Získaj všetky rezervácie
  getAllBookings(): Observable<Booking[]> {
    return this.http.get<Booking[]>(this.apiUrl);
  }

  // Získaj detail rezervácie
  getBookingById(id: number): Observable<Booking> {
    return this.http.get<Booking>(`${this.apiUrl}/${id}`);
  }

  // Vytvor rezerváciu
  createBooking(booking: any): Observable<Booking> {
    return this.http.post<Booking>(this.apiUrl, booking);
  }

  // Zruš rezerváciu
  cancelBooking(id: number): Observable<Booking> {
    return this.http.put<Booking>(`${this.apiUrl}/${id}/cancel`, {});
  }

  // Aktualizuj stav rezervácie (admin)
  updateBookingStatus(id: number, status: string): Observable<Booking> {
    return this.http.put<Booking>(`${this.apiUrl}/${id}/status`, { status });
  }

  // Zmaž rezerváciu (admin)
  deleteBooking(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  // Získaj dostupnosť apartmánu
  getAvailability(apartmentId: number, startDate?: string, endDate?: string): Observable<any> {
    let url = `${this.apiUrl}/availability/${apartmentId}`;
    const params = new URLSearchParams();
    
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    return this.http.get<any>(url);
  }
}