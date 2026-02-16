// src/app/pages/profile/profile.component.ts

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTableModule } from '@angular/material/table';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth.service';
import { BookingService } from '../../services/booking.service';
import { Booking } from '../../models/booking';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatTableModule,
    MatDialogModule,
    MatSnackBarModule
  ],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  user: any = null;
  bookings: Booking[] = [];
  loading = true;
  displayedColumns: string[] = ['apartment', 'dates', 'adults', 'kids', 'total', 'status', 'actions'];

  constructor(
    private authService: AuthService,
    private bookingService: BookingService,
    private router: Router,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.loadUserProfile();
    this.loadBookings();
  }

  loadUserProfile(): void {
    this.authService.getCurrentUser().subscribe({
      next: (user) => {
        this.user = user;
      },
      error: (error) => {
        console.error('Chyba pri načítaní profilu:', error);
        this.snackBar.open('Chyba pri načítaní profilu', 'Zavrieť', { duration: 3000 });
        this.router.navigate(['/login']);
      }
    });
  }

  loadBookings(): void {
    this.loading = true;
    this.bookingService.getMyBookings().subscribe({
      next: (bookings) => {
        this.bookings = bookings;
        this.loading = false;
      },
      error: (error) => {
        console.error('Chyba pri načítaní rezervácií:', error);
        this.snackBar.open('Chyba pri načítaní rezervácií', 'Zavrieť', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  cancelBooking(booking: Booking): void {
    if (confirm(`Naozaj chcete zrušiť rezerváciu pre ${booking.apartment?.name}?`)) {
      this.bookingService.cancelBooking(booking.id).subscribe({
        next: () => {
          this.snackBar.open('Rezervácia bola zrušená', 'Zavrieť', { duration: 3000 });
          this.loadBookings(); // Obnov zoznam
        },
        error: (error) => {
          console.error('Chyba pri rušení rezervácie:', error);
          this.snackBar.open('Chyba pri rušení rezervácie', 'Zavrieť', { duration: 3000 });
        }
      });
    }
  }

  getStatusColor(status: string): string {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return 'primary';
      case 'pending':
        return 'accent';
      case 'cancelled':
        return 'warn';
      default:
        return '';
    }
  }

  getStatusText(status: string): string {
    switch (status?.toLowerCase()) {
      case 'confirmed':
        return 'Potvrdené';
      case 'pending':
        return 'Čaká na potvrdenie';
      case 'cancelled':
        return 'Zrušené';
      default:
        return status;
    }
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('sk-SK');
  }

  canCancelBooking(booking: Booking): boolean {
    // Môžeš zrušiť len ak nie je už zrušená a check-in je v budúcnosti
    const now = new Date();
    const checkIn = new Date(booking.check_in_date);
    return booking.status !== 'cancelled' && checkIn > now;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}