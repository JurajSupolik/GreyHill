// src/app/pages/contact/contact.component.ts

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatSnackBarModule
  ],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.css'
})
export class ContactComponent {
  
  contactForm = {
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  };

  constructor(private snackBar: MatSnackBar) {}

  onSubmit(): void {
    // Validácia
    if (!this.contactForm.name || !this.contactForm.email || !this.contactForm.message) {
      this.snackBar.open('Vyplňte prosím všetky povinné polia', 'Zavrieť', {
        duration: 3000
      });
      return;
    }

    // Tu by sa normálne poslal request na backend
    console.log('Odosielam formulár:', this.contactForm);

    // Zobrazenie úspechu
    this.snackBar.open('Správa bola úspešne odoslaná! Ozveme sa vám čoskoro.', 'OK', {
      duration: 5000
    });

    // Reset formulára
    this.contactForm = {
      name: '',
      email: '',
      phone: '',
      subject: '',
      message: ''
    };
  }
}
