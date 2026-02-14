// src/app/pages/register/register.component.ts

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule
  ],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  userData = {
    email: '',
    username: '',
    full_name: '',
    phone: '',  // ← NOVÝ RIADOK
    password: '',
    confirmPassword: ''
  };

  loading = false;
  hidePassword = true;
  hideConfirmPassword = true;

  constructor(
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {}

  onSubmit(): void {
    // Validácia
    if (!this.userData.email || !this.userData.username || !this.userData.phone || !this.userData.password) {
      this.snackBar.open('Vyplňte všetky povinné polia', 'Zavrieť', { duration: 3000 });
      return;
    }

    // Validácia telefónu
    const phoneRegex = /^\+?[0-9\s]{9,20}$/;
    if (!phoneRegex.test(this.userData.phone)) {
      this.snackBar.open('Neplatné telefónne číslo', 'Zavrieť', { duration: 3000 });
      return;
    }

    if (this.userData.password !== this.userData.confirmPassword) {
      this.snackBar.open('Heslá sa nezhodujú', 'Zavrieť', { duration: 3000 });
      return;
    }

    if (this.userData.password.length < 6) {
      this.snackBar.open('Heslo musí mať aspoň 6 znakov', 'Zavrieť', { duration: 3000 });
      return;
    }

    this.loading = true;

    const registerData = {
      email: this.userData.email,
      username: this.userData.username,
      full_name: this.userData.full_name,
      phone: this.userData.phone,  // ← NOVÝ RIADOK
      password: this.userData.password
    };

    this.authService.register(registerData).subscribe({
      next: (user) => {
        this.loading = false;
        this.snackBar.open('Registrácia úspešná! Teraz sa môžete prihlásiť.', 'OK', { duration: 5000 });
        this.router.navigate(['/login']);
      },
      error: (error) => {
        this.loading = false;
        const errorMessage = error.error?.detail || 'Chyba pri registrácii';
        this.snackBar.open(errorMessage, 'Zavrieť', { duration: 5000 });
      }
    });
  }
}