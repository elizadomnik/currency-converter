import { CommonModule } from "@angular/common";
import { Component, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from "@angular/material/card";
import {
  MatDatepickerInputEvent,
  MatDatepickerModule,
} from "@angular/material/datepicker";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIconModule } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatTableModule } from "@angular/material/table";
import {
  Currency,
  CurrencyService,
  RateWithCurrency,
} from "../../services/currency.service";

@Component({
  selector: "app-currency-dashboard",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatDatepickerModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatIconModule,
  ],
  templateUrl: "./currency-dashboard.component.html",
  styles: [
    `
      .dashboard-container {
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
      }
      .controls {
        display: flex;
        gap: 20px;
        align-items: center;
        margin-bottom: 20px;
      }
      .spinner-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
      }
      table {
        width: 100%;
      }
      .status-message {
        margin-top: 10px;
        color: #666;
      }
      .date-info {
        margin: 15px 0;
        color: #666;
      }

      .mat-mdc-card-header {
        padding: 16px;
      }
    `,
  ],
})
export class CurrencyDashboardComponent implements OnInit {
  selectedDate: Date = new Date();
  rates: RateWithCurrency[] = [];
  currencies: Currency[] = [];
  loading: boolean = false;
  message: string = "";
  displayedColumns: string[] = ["code", "name", "rate", "date"];

  constructor(private currencyService: CurrencyService) {}

  ngOnInit() {
    this.loadCurrencies();
    this.loadRates();
  }

  onDateChange(event: MatDatepickerInputEvent<Date>) {
    if (event.value) {
      this.selectedDate = event.value;
      this.loadRates();
    }
  }

  formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const day = date.getDate().toString().padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  loadCurrencies() {
    this.currencyService.getCurrencies().subscribe({
      next: (data) => (this.currencies = data),
      error: () => (this.message = "Nie udało się załadować listy walut."),
    });
  }

  fetchFromNbp() {
    this.loading = true;
    const dateStr = this.formatDate(this.selectedDate);
    this.message = `Pobieranie danych z NBP dla daty ${dateStr}...`;
    this.currencyService.fetchRatesFromNbp(dateStr).subscribe({
      next: (res) => {
        this.message = res.message;
        this.loadRates();
      },
      error: (err) => {
        this.message =
          "Błąd podczas synchronizacji z API NBP. Sprawdź czy data nie przypada w weekend/święto.";
        this.loading = false;
      },
    });
  }

  loadRates() {
    this.loading = true;
    const dateStr = this.formatDate(this.selectedDate);
    this.currencyService.getRatesByDate(dateStr).subscribe({
      next: (data) => {
        this.rates = data;
        this.loading = false;
        if (data.length === 0) {
          this.message = `Brak danych dla daty ${dateStr}. Spróbuj pobrać najnowsze dane
            klikając przycisk "Synchornizuj z NBP" w celu pobrania kursów walut z danego dnia lub zmień datę.`;
        } else {
          this.message = "";
        }
      },
      error: (err) => {
        this.message = "Błąd podczas ładowania kursów z bazy.";
        this.loading = false;
      },
    });
  }

  getQuarter(date: Date): number {
    return Math.floor(date.getMonth() / 3) + 1;
  }

  getYear(date: Date): number {
    return date.getFullYear();
  }

  getMonth(date: Date): number {
    return date.getMonth() + 1;
  }

  getDay(date: Date): number {
    return date.getDate();
  }
}
