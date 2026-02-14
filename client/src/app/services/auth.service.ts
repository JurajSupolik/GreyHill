// src/app/services/auth.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  phone?: string;  // ← PRIDANÉ
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name?: string;
  phone: string;  // ← PRIDANÉ
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Pri načítaní aplikácie skontroluj, či je používateľ prihlásený
    this.checkAuth();
  }

  // Registrácia
  register(data: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${this.apiUrl}/register`, data);
  }

  // Prihlásenie
  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login-json`, credentials).pipe(
      tap(response => {
        console.log('🔑 Login response:', response);
        // Ulož token do localStorage
        localStorage.setItem('access_token', response.access_token);
        // Nastav aktuálneho používateľa
        this.currentUserSubject.next(response.user);
        console.log('✅ User set:', response.user);
      })
    );
  }

  // Odhlásenie
  logout(): void {
    localStorage.removeItem('access_token');
    this.currentUserSubject.next(null);
    this.router.navigate(['/']);
  }

  // Získaj token
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // Je používateľ prihlásený?
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Je používateľ admin?
  isAdmin(): boolean {
    const user = this.currentUserSubject.value;
    return user?.is_admin || false;
  }

  // Získaj aktuálneho používateľa z API
  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/me`).pipe(
      tap(user => {
        console.log('👤 Current user from API:', user);
        this.currentUserSubject.next(user);
      })
    );
  }

  // Skontroluj autentifikáciu pri načítaní aplikácie
  private checkAuth(): void {
    if (this.isAuthenticated()) {
      this.getCurrentUser().subscribe({
        next: (user) => {
          console.log('✅ Auth check passed, user loaded');
        },
        error: () => {
          console.log('❌ Auth check failed, logging out');
          // Ak token je neplatný, odhláš používateľa
          this.logout();
        }
      });
    }
  }

  // Getter pre aktuálneho používateľa
  get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }
}