// src/app/components/apartment-card/apartment-card.component.ts

import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { Apartment } from '../../models/apartment';

@Component({
  selector: 'app-apartment-card',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule
  ],
  templateUrl: './apartment-card.component.html',
  styleUrl: './apartment-card.component.css'
})
export class ApartmentCardComponent {
  @Input() apartment!: Apartment;
}