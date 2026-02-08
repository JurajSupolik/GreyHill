// src/app/pages/admin/dashboard/dashboard.component.ts

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';  // ← PRIDAJ TENTO IMPORT!
import { BookingService } from '../../../services/booking.service';
import { Booking, BookingStatus } from '../../../models/booking';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatChipsModule,
    MatMenuModule,
    MatSnackBarModule,
    MatDialogModule,
    MatDividerModule  // ← A PRIDAJ SEM!
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  bookings: Booking[] = [];
  loading = true;
  displayedColumns: string[] = ['id', 'guestName', 'apartmentId', 'checkIn', 'checkOut', 'guests', 'price', 'status', 'actions'];

  constructor(
    private bookingService: BookingService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadBookings();
  }

  loadBookings(): void {
    this.loading = true;
    this.bookingService.getAllBookings().subscribe({
      next: (bookings) => {
        this.bookings = bookings;
        this.loading = false;
      },
      error: (error) => {
        console.error('Chyba pri načítaní rezervácií:', error);
        this.snackBar.open('❌ Chyba pri načítaní rezervácií', 'Zavrieť', {
          duration: 3000
        });
        this.loading = false;
      }
    });
  }

  // ← PRIDAJ TIETO FUNKCIE:
  get pendingCount(): number {
    return this.bookings.filter(b => b.status === 'PENDING').length;
  }

  get confirmedCount(): number {
    return this.bookings.filter(b => b.status === 'CONFIRMED').length;
  }

  getStatusColor(status: string): string {
    switch(status) {
      case 'PENDING': return 'warn';
      case 'CONFIRMED': return 'primary';
      case 'CANCELLED': return 'accent';
      case 'COMPLETED': return '';
      default: return '';
    }
  }

  getStatusText(status: string): string {
    switch(status) {
      case 'PENDING': return 'Čaká';
      case 'CONFIRMED': return 'Potvrdená';
      case 'CANCELLED': return 'Zrušená';
      case 'COMPLETED': return 'Dokončená';
      default: return status;
    }
  }

  changeStatus(bookingId: number, newStatus: string): void {
    if (confirm(`Naozaj chcete zmeniť status na "${this.getStatusText(newStatus)}"?`)) {
      this.bookingService.updateBookingStatus(bookingId, newStatus).subscribe({
        next: () => {
          this.snackBar.open('✅ Status zmenený', 'Zavrieť', { duration: 3000 });
          this.loadBookings(); // Refresh
        },
        error: (error: any) => {
          this.snackBar.open('❌ Chyba pri zmene statusu', 'Zavrieť', { duration: 3000 });
          console.error('Chyba:', error);
        }
      });
    }
  }

  confirmBooking(bookingId: number): void {
    this.changeStatus(bookingId, 'CONFIRMED');
  }

  cancelBooking(bookingId: number): void {
    this.changeStatus(bookingId, 'CANCELLED');
  }

  deleteBooking(bookingId: number): void {
    if (confirm('⚠️ Naozaj chcete NATRVALO zmazať túto rezerváciu? Táto akcia sa nedá vrátiť späť!')) {
      this.bookingService.deleteBooking(bookingId).subscribe({
        next: () => {
          this.snackBar.open('🗑️ Rezervácia zmazaná', 'Zavrieť', { duration: 3000 });
          this.loadBookings(); // Refresh
        },
        error: (error) => {
          this.snackBar.open('❌ Chyba pri mazaní', 'Zavrieť', { duration: 3000 });
          console.error('Chyba:', error);
        }
      });
    }
  }

  formatDate(date: Date | string): string {
    const d = new Date(date);
    return d.toLocaleDateString('sk-SK', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}