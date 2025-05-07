import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private isAuthenticated = false;

  constructor(private router: Router) {}

  login(username: string, password: string): boolean {
    // Dummy check for username and password
    if ((username === 'admin' && password === 'admin') ||
        (username === 'Belthangady' && password === 'Belthangady@123') ||
        (username === 'Chamrajnagar' && password === 'Chamrajnagar@123') ||
        (username === 'Chikkamangalur' && password === 'Chikkamangalur@123') ||
        (username === 'Gonikkoppa' && password === 'Gonikkoppa@123') ||
        (username === 'HassanWh' && password === 'HassanWh@123') ||
        (username === 'Hassan' && password === 'Hassan@123') ||
        (username === 'HassanRO' && password === 'HassanRO@123') ||
        (username === 'Kadur' && password === 'Kadur@123') ||
        (username === 'Koppa' && password === 'Koppa@123') ||
        (username === 'Kundapura' && password === 'Kundapura@123') ||
        (username === 'Madikeri' && password === 'Madikeri@123') ||
        (username === 'Mandaya' && password === 'Mandaya@123') ||
        (username === 'MangaloreWh' && password === 'MangaloreWh@123') ||
        (username === 'Pumpwell' && password === 'Pumpwell@123') ||
        (username === 'MysoreWh' && password === 'MysoreWh@123') ||
        (username === 'MysoreKuvempunagar' && password === 'MysoreKuvempunagar@123') ||
        (username === 'MysoreCityRO' && password === 'MysoreCityRO@123') ||
        (username === 'Puttur' && password === 'Puttur@123') ||
        (username === 'UdupiWh' && password === 'UdupiWh@123') ||
        (username === 'UdupiRO' && password === 'UdupiRO@123') ||
        (username === 'superuser' && password === 'superuser')) {
      this.isAuthenticated = true;
      localStorage.setItem('isAuthenticated', 'true');  // Store in localStorage
      return true;
    } else {
      this.isAuthenticated = false;
      localStorage.setItem('isAuthenticated', 'false');
      return false;
    }
  }

  logout(): void {
    this.isAuthenticated = false;
    localStorage.setItem('isAuthenticated', 'false');
    this.router.navigate(['/auth/login']);
  }

  getAuthStatus(): boolean {
    return localStorage.getItem('isAuthenticated') === 'true';
  }
}
