
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { Apartment } from '../../models/apartment';
import { ApartmentService } from '../../services/apartment.service';
import { ApartmentCardComponent } from '../apartment-card/apartment-card.component';

@Component({
  selector: 'app-apartment-list',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    ApartmentCardComponent
  ],
  templateUrl: './apartment-list.component.html',
  styleUrl: './apartment-list.component.css'
})
export class ApartmentListComponent implements OnInit {
  apartments: Apartment[] = [];
  loading: boolean = true;

  constructor(private apartmentService: ApartmentService) { }

  ngOnInit(): void {
    this.loadApartments();
  }

  loadApartments(): void {
    this.apartmentService.getApartments().subscribe({
      next: (data) => {
        this.apartments = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Chyba:', error);
        this.loading = false;
      }
    });
  }
}