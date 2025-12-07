// src/app/services/apartment.service.ts

import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Apartment } from '../models/apartment';

@Injectable({
  providedIn: 'root'
})
export class ApartmentService {

  private mockApartments: Apartment[] = [
    {
      id: 1,
      name: 'Luxusný apartmán centrum',
      description: 'Krásny priestranný apartmán v centre mesta s výhľadom na hory.',
      pricePerNight: 89,
      capacity: 4,
      bedrooms: 2,
      bathrooms: 1,
      imageUrl: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800',
      amenities: ['WiFi', 'TV', 'Kuchyňa', 'Parking', 'Balkón'],
      address: 'Hlavná 123',
      city: 'Bratislava',
      rating: 4.8
    },
    {
      id: 2,
      name: 'Moderný loft s terasou',
      description: 'Štýlový loft s veľkou terasou, ideálny pre páry.',
      pricePerNight: 120,
      capacity: 2,
      bedrooms: 1,
      bathrooms: 1,
      imageUrl: 'https://images.unsplash.com/photo-1502672260066-6bc36a69ce48?w=800',
      amenities: ['WiFi', 'TV', 'Kuchyňa', 'Terasa', 'Klimatizácia'],
      address: 'Dunajská 45',
      city: 'Bratislava',
      rating: 4.9
    },
    {
      id: 3,
      name: 'Rodinný apartmán s garážou',
      description: 'Priestranný 3-izbový apartmán pre celú rodinu.',
      pricePerNight: 150,
      capacity: 6,
      bedrooms: 3,
      bathrooms: 2,
      imageUrl: 'https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800',
      amenities: ['WiFi', 'TV', 'Kuchyňa', 'Parking', 'Garáž', 'Záhrada'],
      address: 'Lesná 78',
      city: 'Košice',
      rating: 4.7
    }
  ];

  constructor() { }

  getApartments(): Observable<Apartment[]> {
    return of(this.mockApartments);
  }

  getApartmentById(id: number): Observable<Apartment | undefined> {
    const apartment = this.mockApartments.find(apt => apt.id === id);
    return of(apartment);
  }
}