// src/app/services/apartment.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Apartment } from '../models/apartment';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApartmentService {
  private apiUrl = `${environment.apiUrl}/apartments`;

  constructor(private http: HttpClient) { }

  // Získaj všetky apartmány
  getApartments(city?: string, skip: number = 0, limit: number = 100): Observable<Apartment[]> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());

    if (city) {
      params = params.set('city', city);
    }

    return this.http.get<Apartment[]>(this.apiUrl, { params });
  }

  // Získaj jeden apartmán podľa ID
  getApartmentById(id: number): Observable<Apartment> {
    return this.http.get<Apartment>(`${this.apiUrl}/${id}`);
  }

  // Vytvor nový apartmán (len pre adminov)
  createApartment(apartment: Apartment): Observable<Apartment> {
    return this.http.post<Apartment>(this.apiUrl, apartment);
  }

  // Uprav apartmán (len pre adminov)
  updateApartment(id: number, apartment: Partial<Apartment>): Observable<Apartment> {
    return this.http.put<Apartment>(`${this.apiUrl}/${id}`, apartment);
  }

  // Zmaž apartmán (len pre adminov)
  deleteApartment(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  // Získaj dostupnosť apartmánu pre kalendár
  getApartmentAvailability(id: number, startDate?: string, endDate?: string): Observable<any> {
    let params = new HttpParams();
    if (startDate) params = params.set('start_date', startDate);
    if (endDate) params = params.set('end_date', endDate);
    
    return this.http.get<any>(`${this.apiUrl}/../bookings/availability/${id}`, { params });
  }
}