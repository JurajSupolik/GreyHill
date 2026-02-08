// src/app/pages/apartment-detail/apartment-detail.component.ts
import { AvailabilityCalendarComponent } from '../../components/availability-calendar/availability-calendar.component';
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApartmentService } from '../../services/apartment.service';
import { BookingService } from '../../services/booking.service';
import { Apartment } from '../../models/apartment';

@Component({
  selector: 'app-apartment-detail',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDividerModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatSnackBarModule,
    AvailabilityCalendarComponent  // ← PRIDAJ TOTO!
  ],
  templateUrl: './apartment-detail.component.html',
  styleUrl: './apartment-detail.component.css'
})
export class ApartmentDetailComponent implements OnInit {
  apartment: Apartment | null = null;
  loading = true;
  error = false;
  bookingForm: FormGroup;
  showBookingForm = false;
  submitting = false;
  minDate = new Date();
  totalPrice: number = 0;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apartmentService: ApartmentService,
    private bookingService: BookingService,
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ) {
    // Inicializuj formulár
    this.bookingForm = this.fb.group({
      guestName: ['', [Validators.required, Validators.minLength(2)]],
      guestEmail: ['', [Validators.required, Validators.email]],
      guestPhone: ['', [Validators.required, Validators.pattern(/^[0-9+\s()-]{9,}$/)]],
      checkInDate: ['', Validators.required],
      checkOutDate: ['', Validators.required],
      numberOfGuests: [1, [Validators.required, Validators.min(1)]],
      specialRequests: ['']
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    
    if (id) {
      this.loadApartment(+id);
    } else {
      this.error = true;
      this.loading = false;
    }

    // Počúvaj zmeny v dátumoch pre výpočet ceny
    this.bookingForm.get('checkInDate')?.valueChanges.subscribe(() => this.calculatePrice());
    this.bookingForm.get('checkOutDate')?.valueChanges.subscribe(() => this.calculatePrice());
  }

  loadApartment(id: number): void {
    this.apartmentService.getApartmentById(id).subscribe({
      next: (apartment) => {
        if (apartment) {
          this.apartment = apartment;
          // Nastav max počet hostí podľa kapacity apartmánu
          this.bookingForm.get('numberOfGuests')?.setValidators([
            Validators.required,
            Validators.min(1),
            Validators.max(apartment.capacity)
          ]);
        } else {
          this.error = true;
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Chyba pri načítaní apartmánu:', error);
        this.error = true;
        this.loading = false;
      }
    });
  }

  calculatePrice(): void {
    const checkIn = this.bookingForm.get('checkInDate')?.value;
    const checkOut = this.bookingForm.get('checkOutDate')?.value;

    if (checkIn && checkOut && this.apartment) {
      const days = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
      if (days > 0) {
        this.totalPrice = days * this.apartment.price_per_night;
      } else {
        this.totalPrice = 0;
      }
    }
  }

  goBack(): void {
    this.router.navigate(['/apartments']);
  }

  toggleBookingForm(): void {
    this.showBookingForm = !this.showBookingForm;
  }

  submitBooking(): void {
    if (this.bookingForm.valid && this.apartment) {
      this.submitting = true;

      const bookingData = {
        apartment_id: this.apartment.id,
        guest_name: this.bookingForm.value.guestName,
        guest_email: this.bookingForm.value.guestEmail,
        guest_phone: this.bookingForm.value.guestPhone,
        check_in_date: this.bookingForm.value.checkInDate.toISOString(),
        check_out_date: this.bookingForm.value.checkOutDate.toISOString(),
        number_of_guests: this.bookingForm.value.numberOfGuests,
        special_requests: this.bookingForm.value.specialRequests || ''
      };

      this.bookingService.createBooking(bookingData).subscribe({
        next: (response) => {
          this.submitting = false;
          this.snackBar.open('✅ Rezervácia úspešne vytvorená!', 'Zavrieť', {
            duration: 5000,
            horizontalPosition: 'center',
            verticalPosition: 'top'
          });
          this.bookingForm.reset();
          this.showBookingForm = false;
          this.totalPrice = 0;
        },
        error: (error) => {
          this.submitting = false;
          const errorMessage = error.error?.detail || 'Chyba pri vytváraní rezervácie';
          this.snackBar.open(`❌ ${errorMessage}`, 'Zavrieť', {
            duration: 5000,
            horizontalPosition: 'center',
            verticalPosition: 'top'
          });
          console.error('Chyba pri rezervácii:', error);
        }
      });
    } else {
      this.snackBar.open('⚠️ Prosím vyplňte všetky povinné polia správne', 'Zavrieť', {
        duration: 3000
      });
    }
  }
}