import {
  ComponentFixture,
  TestBed,
  fakeAsync,
  tick,
} from "@angular/core/testing";
import { provideNativeDateAdapter } from "@angular/material/core";
import { MatDatepickerInputEvent } from "@angular/material/datepicker";
import { By } from "@angular/platform-browser";
import { NoopAnimationsModule } from "@angular/platform-browser/animations";
import { of, throwError } from "rxjs";
import { delay } from "rxjs/operators";
import {
  Currency,
  CurrencyService,
  RateWithCurrency,
} from "../../services/currency.service";
import { CurrencyDashboardComponent } from "./currency-dashboard.component";

describe("CurrencyDashboardComponent", () => {
  let component: CurrencyDashboardComponent;
  let fixture: ComponentFixture<CurrencyDashboardComponent>;
  let currencyServiceSpy: jasmine.SpyObj<CurrencyService>;

  const mockCurrencies: Currency[] = [
    { id: 1, code: "USD", name: "US Dollar" },
    { id: 2, code: "EUR", name: "Euro" },
  ];

  const mockRates: RateWithCurrency[] = [
    {
      date: "2023-01-01",
      rate: 3.5,
      currency: { code: "USD", name: "US Dollar" },
    },
    { date: "2023-01-01", rate: 4.5, currency: { code: "EUR", name: "Euro" } },
  ];

  beforeEach(async () => {
    const spy = jasmine.createSpyObj("CurrencyService", [
      "getCurrencies",
      "getRatesByDate",
      "fetchRatesFromNbp",
    ]);

    await TestBed.configureTestingModule({
      imports: [CurrencyDashboardComponent, NoopAnimationsModule],
      providers: [
        { provide: CurrencyService, useValue: spy },
        provideNativeDateAdapter(),
      ],
    }).compileComponents();

    currencyServiceSpy = TestBed.inject(
      CurrencyService,
    ) as jasmine.SpyObj<CurrencyService>;

    currencyServiceSpy.getCurrencies.and.returnValue(of(mockCurrencies));
    currencyServiceSpy.getRatesByDate.and.returnValue(of([]));
    currencyServiceSpy.fetchRatesFromNbp.and.returnValue(
      of({ message: "Success" }),
    );

    fixture = TestBed.createComponent(CurrencyDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  describe("Initialization", () => {
    it("should load currencies on init", () => {
      expect(currencyServiceSpy.getCurrencies).toHaveBeenCalled();
      expect(component.currencies.length).toBe(2);
      expect(component.currencies).toEqual(mockCurrencies);
    });

    it("should attempt to load rates for default date on init", () => {
      expect(currencyServiceSpy.getRatesByDate).toHaveBeenCalled();
    });
  });

  describe("Feature: Fetching Data from NBP", () => {
    it("should call fetchRatesFromNbp when fetchFromNbp method is triggered", fakeAsync(() => {
      currencyServiceSpy.fetchRatesFromNbp.and.returnValue(
        of({ message: "Success" }).pipe(delay(100)),
      );

      component.selectedDate = new Date("2023-10-10");
      component.fetchFromNbp();

      expect(component.loading).toBeTrue();
      expect(currencyServiceSpy.fetchRatesFromNbp).toHaveBeenCalledWith(
        "2023-10-10",
      );

      tick(100);
      expect(component.loading).toBeFalse();
    }));

    it("should reload rates after successful fetch", fakeAsync(() => {
      component.selectedDate = new Date("2023-10-10");
      currencyServiceSpy.getRatesByDate.calls.reset();

      currencyServiceSpy.getRatesByDate.and.returnValue(of(mockRates));

      component.fetchFromNbp();

      tick();

      expect(currencyServiceSpy.getRatesByDate).toHaveBeenCalledWith(
        "2023-10-10",
      );

      expect(component.rates).toEqual(mockRates);
      expect(component.message).toBe("");
    }));

    it("should handle errors during fetch", fakeAsync(() => {
      currencyServiceSpy.fetchRatesFromNbp.and.returnValue(
        throwError(() => new Error("API Error")),
      );

      component.fetchFromNbp();
      tick();

      expect(component.message).toContain("Błąd podczas synchronizacji");
      expect(component.loading).toBeFalse();
    }));
  });

  describe("Feature: Date Selection", () => {
    it("should update rates when date is changed via method", () => {
      const newDate = new Date("2025-01-01");
      currencyServiceSpy.getRatesByDate.calls.reset();
      currencyServiceSpy.getRatesByDate.and.returnValue(of(mockRates));

      const event = { value: newDate } as MatDatepickerInputEvent<Date>;
      component.onDateChange(event);

      expect(component.selectedDate).toEqual(newDate);
      expect(currencyServiceSpy.getRatesByDate).toHaveBeenCalledWith(
        "2025-01-01",
      );
      expect(component.rates).toEqual(mockRates);
    });
  });

  describe("Feature: Dashboard Display", () => {
    it("should display table when rates are available", () => {
      component.rates = mockRates;
      fixture.detectChanges();

      const tableRows = fixture.debugElement.queryAll(By.css("tr[mat-row]"));
      expect(tableRows.length).toBe(2);
    });

    it("should show spinner when loading", () => {
      component.loading = true;
      fixture.detectChanges();
      const spinner = fixture.debugElement.query(By.css("mat-spinner"));
      expect(spinner).toBeTruthy();
    });
  });
});
