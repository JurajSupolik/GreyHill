// src/app/components/availability-calendar/availability-calendar.component.ts

import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { ApartmentService } from '../../services/apartment.service';

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isOccupied: boolean;
  isToday: boolean;
}

@Component({
  selector: 'app-availability-calendar',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  templateUrl: './availability-calendar.component.html',
  styleUrl: './availability-calendar.component.css'
})
export class AvailabilityCalendarComponent implements OnInit {
  @Input() apartmentId!: number;
  
  currentMonth: Date = new Date();
  calendarDays: CalendarDay[] = [];
  occupiedDates: Set<string> = new Set();
  loading = true;
  
  weekDays = ['Po', 'Ut', 'St', 'Št', 'Pi', 'So', 'Ne'];
  monthNames = [
    'Január', 'Február', 'Marec', 'Apríl', 'Máj', 'Jún',
    'Júl', 'August', 'September', 'Október', 'November', 'December'
  ];

  constructor(private apartmentService: ApartmentService) {}

  ngOnInit(): void {
    this.loadAvailability();
  }

  loadAvailability(): void {
    this.loading = true;
    
    // Získaj data pre +/- 1 mesiac
    const start = new Date(this.currentMonth);
    start.setMonth(start.getMonth() - 1);
    
    const end = new Date(this.currentMonth);
    end.setMonth(end.getMonth() + 2);
    
    this.apartmentService.getApartmentAvailability(
      this.apartmentId,
      start.toISOString().split('T')[0],
      end.toISOString().split('T')[0]
    ).subscribe({
      next: (data) => {
        console.log('📅 Dostupnosť z API:', data); // DEBUG
        
        // Spracuj booked_dates z backendu
        this.occupiedDates = new Set();
        
        if (data.booked_dates && Array.isArray(data.booked_dates)) {
          data.booked_dates.forEach((booking: any) => {
            // Pridaj všetky dni medzi check_in a check_out
            const checkIn = new Date(booking.check_in);
            const checkOut = new Date(booking.check_out);
            
            let currentDate = new Date(checkIn);
            while (currentDate < checkOut) {
              const dateStr = currentDate.toISOString().split('T')[0];
              this.occupiedDates.add(dateStr);
              currentDate.setDate(currentDate.getDate() + 1);
            }
          });
        }
        
        console.log('🔴 Obsadené dni:', Array.from(this.occupiedDates)); // DEBUG
        
        this.generateCalendar();
        this.loading = false;
      },
      error: (error) => {
        console.error('Chyba pri načítaní dostupnosti:', error);
        this.loading = false;
      }
    });
  }

  generateCalendar(): void {
    this.calendarDays = [];
    
    const year = this.currentMonth.getFullYear();
    const month = this.currentMonth.getMonth();
    
    // Prvý deň mesiaca
    const firstDay = new Date(year, month, 1);
    // Posledný deň mesiaca
    const lastDay = new Date(year, month + 1, 0);
    
    // Deň v týždni prvého dňa (0 = nedeľa, 6 = sobota)
    let startDayOfWeek = firstDay.getDay();
    // Prekonvertuj na (0 = pondelok, 6 = nedeľa)
    startDayOfWeek = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1;
    
    // Dni z predchádzajúceho mesiaca
    for (let i = startDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month, -i);
      this.calendarDays.push({
        date: date,
        isCurrentMonth: false,
        isOccupied: this.isDateOccupied(date),
        isToday: this.isToday(date)
      });
    }
    
    // Dni aktuálneho mesiaca
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      this.calendarDays.push({
        date: date,
        isCurrentMonth: true,
        isOccupied: this.isDateOccupied(date),
        isToday: this.isToday(date)
      });
    }
    
    // Dni z nasledujúceho mesiaca (aby sme doplnili riadky)
    const remainingDays = 42 - this.calendarDays.length; // 6 týždňov × 7 dní
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month + 1, day);
      this.calendarDays.push({
        date: date,
        isCurrentMonth: false,
        isOccupied: this.isDateOccupied(date),
        isToday: this.isToday(date)
      });
    }
  }

  isDateOccupied(date: Date): boolean {
    const dateStr = date.toISOString().split('T')[0];
    const isOccupied = this.occupiedDates.has(dateStr);
    return isOccupied;
  }

  isToday(date: Date): boolean {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  }

  previousMonth(): void {
    this.currentMonth = new Date(
      this.currentMonth.getFullYear(),
      this.currentMonth.getMonth() - 1,
      1
    );
    this.loadAvailability();
  }

  nextMonth(): void {
    this.currentMonth = new Date(
      this.currentMonth.getFullYear(),
      this.currentMonth.getMonth() + 1,
      1
    );
    this.loadAvailability();
  }

  get currentMonthName(): string {
    return `${this.monthNames[this.currentMonth.getMonth()]} ${this.currentMonth.getFullYear()}`;
  }
}