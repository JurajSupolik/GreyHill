// src/app/app.routes.ts

import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { ApartmentListComponent } from './components/apartment-list/apartment-list.component';
import { ApartmentDetailComponent } from './pages/apartment-detail/apartment-detail.component';
import { AboutComponent } from './pages/about/about.component';
import { ContactComponent } from './pages/contact/contact.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { DashboardComponent } from './pages/admin/dashboard/dashboard.component';
import { TestComponent } from './pages/test/test.component';
import { adminGuard } from './guards/auth.guard';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'apartments', component: ApartmentListComponent },
  { path: 'apartments/:id', component: ApartmentDetailComponent },
  { path: 'about', component: AboutComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'test', component: TestComponent },
  { 
    path: 'profile', 
    component: ProfileComponent,
    canActivate: [authGuard]  // Len prihlásení môžu vidieť profil
  },
  { 
    path: 'admin', 
    component: DashboardComponent,
    canActivate: [adminGuard]
  },
  { path: '**', redirectTo: '' }
];