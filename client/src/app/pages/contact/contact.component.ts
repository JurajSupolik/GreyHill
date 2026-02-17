import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select'; 
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ContactService } from '../../services/contact.service'; 

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule, 
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

  submitting = false; 

  constructor(
    private snackBar: MatSnackBar,
    private contactService: ContactService 
  ) {}

  onSubmit(): void {
    // Validácia
    if (!this.contactForm.name || !this.contactForm.email || !this.contactForm.message) {
      this.snackBar.open('❌ Vyplňte prosím všetky povinné polia', 'Zavrieť', {
        duration: 3000
      });
      return;
    }

   
   // Email validácia
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(this.contactForm.email)) {
  this.snackBar.open('❌ Zadajte platný email', 'Zavrieť', {
    duration: 3000
  });
  return;
}

    this.submitting = true;

    // Odoslanie na backend
    this.contactService.sendMessage(this.contactForm).subscribe({
      next: (response) => {
        console.log('✅ Odpoveď z backendu:', response);
        
        this.snackBar.open('✅ ' + response.message, 'OK', {
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
        
        this.submitting = false;
      },
      error: (error) => {
        console.error('❌ Chyba pri odosielaní:', error);
        
        const errorMsg = error.error?.detail || 'Chyba pri odosielaní správy. Skúste to prosím neskôr.';
        this.snackBar.open('❌ ' + errorMsg, 'Zavrieť', {
          duration: 5000
        });
        
        this.submitting = false;
      }
    });
  }
}