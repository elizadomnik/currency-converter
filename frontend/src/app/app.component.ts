import { Component } from '@angular/core';
import { CurrencyDashboardComponent } from './components/currency-dashboard/currency-dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CurrencyDashboardComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'Currency Converter';
}
