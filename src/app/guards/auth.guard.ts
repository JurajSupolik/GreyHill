// src/app/guards/auth.guard.ts

import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

// Guard pre prihlásených používateľov
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Ak nie je prihlásený, presmeruj na login
  router.navigate(['/login'], { queryParams: { returnUrl: state.url } });
  return false;
};

// Guard pre adminov
export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated() && authService.isAdmin()) {
    return true;
  }

  // Ak nie je admin, presmeruj na home
  router.navigate(['/']);
  return false;
};
