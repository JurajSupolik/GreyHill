import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-test-api',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './test-api.component.html',
  styleUrls: ['./test-api.component.css']
})
export class TestApiComponent {
  //url: string = '';
  //url: string = 'https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m';
  url: string = 'https://greyhill-api.azurewebsites.net/api/apartments/1';  
  response: string = '';
  loading: boolean = false;
  error: string = '';

  constructor(private http: HttpClient) {}

  testApi(): void {
    if (!this.url.trim()) {
      this.error = 'Prosím, zadaj URL';
      return;
    }

    this.loading = true;
    this.error = '';
    this.response = '';
    //this.url = ''; //nemaz url

    this.http.get(this.url, { responseType: 'text' }).subscribe({
      next: (data) => {
        this.response = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = `Chyba: ${err.status} - ${err.message}`;
        this.loading = false;
      }
    });
  }

  clearResults(): void {
    this.response = '';
    this.error = '';
    this.url = '';
  }
}
