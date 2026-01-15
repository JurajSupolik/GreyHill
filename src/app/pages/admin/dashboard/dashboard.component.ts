// src/app/pages/admin/dashboard/dashboard.component.ts

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { UserService } from '../../../services/user.service';
import { ApartmentService } from '../../../services/apartment.service';
import { User } from '../../../services/auth.service';
import { Apartment } from '../../../models/apartment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatChipsModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  users: User[] = [];
  apartments: Apartment[] = [];
  loading = true;

  // Štatistiky
  stats = {
    totalUsers: 0,
    activeUsers: 0,
    adminUsers: 0,
    totalApartments: 0
  };

  displayedColumns: string[] = ['id', 'username', 'email', 'is_admin', 'is_active', 'created_at'];

  constructor(
    private userService: UserService,
    private apartmentService: ApartmentService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading = true;

    // Načítaj používateľov
    this.userService.getAllUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.calculateStats();
        this.loading = false;
      },
      error: (error) => {
        console.error('Chyba pri načítaní používateľov:', error);
        this.loading = false;
      }
    });

    // Načítaj apartmány
    this.apartmentService.getApartments().subscribe({
      next: (apartments) => {
        this.apartments = apartments;
        this.stats.totalApartments = apartments.length;
      },
      error: (error) => {
        console.error('Chyba pri načítaní apartmánov:', error);
      }
    });
  }

  calculateStats(): void {
    this.stats.totalUsers = this.users.length;
    this.stats.activeUsers = this.users.filter(u => u.is_active).length;
    this.stats.adminUsers = this.users.filter(u => u.is_admin).length;
  }
}