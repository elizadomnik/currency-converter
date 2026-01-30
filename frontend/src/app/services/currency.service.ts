import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Currency {
  id: number;
  code: string;
  name: string;
}

export interface RateWithCurrency {
  date: string;
  rate: number;
  currency: {
    code: string;
    name: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class CurrencyService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  getCurrencies(): Observable<Currency[]> {
    return this.http.get<Currency[]>(`${this.apiUrl}/currencies`);
  }

  getRatesByDate(date: string): Observable<RateWithCurrency[]> {
    return this.http.get<RateWithCurrency[]>(`${this.apiUrl}/currencies/${date}`);
  }

  fetchRatesFromNbp(date?: string): Observable<any> {
    const url = date ? `${this.apiUrl}/currencies/fetch?date=${date}` : `${this.apiUrl}/currencies/fetch`;
    return this.http.post(url, {});
  }
}
