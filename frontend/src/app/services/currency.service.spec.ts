import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CurrencyService, Currency, RateWithCurrency } from './currency.service';

describe('CurrencyService', () => {
  let service: CurrencyService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CurrencyService]
    });
    service = TestBed.inject(CurrencyService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('Method: getCurrencies', () => {
    it('should retrieve a list of currencies via GET', () => {
      const dummyCurrencies: Currency[] = [
        { id: 1, code: 'USD', name: 'US Dollar' },
        { id: 2, code: 'EUR', name: 'Euro' }
      ];

      service.getCurrencies().subscribe(currencies => {
        expect(currencies.length).toBe(2);
        expect(currencies).toEqual(dummyCurrencies);
      });

      const req = httpMock.expectOne('http://localhost:8000/currencies');
      expect(req.request.method).toBe('GET');
      req.flush(dummyCurrencies);
    });
  });

  describe('Method: getRatesByDate', () => {
    it('should retrieve rates for a specific date via GET', () => {
      const date = '2023-10-25';
      const dummyRates: RateWithCurrency[] = [
        { date: '2023-10-25', rate: 4.20, currency: { code: 'USD', name: 'US Dollar' } }
      ];

      service.getRatesByDate(date).subscribe(rates => {
        expect(rates.length).toBe(1);
        expect(rates[0].currency.code).toBe('USD');
      });

      const req = httpMock.expectOne(`http://localhost:8000/currencies/${date}`);
      expect(req.request.method).toBe('GET');
      req.flush(dummyRates);
    });
  });

  describe('Method: fetchRatesFromNbp', () => {
    it('should trigger NBP fetch via POST request', () => {
      const responseMessage = { message: 'Success' };

      service.fetchRatesFromNbp().subscribe(res => {
        expect(res).toEqual(responseMessage);
      });

      const req = httpMock.expectOne('http://localhost:8000/currencies/fetch');
      expect(req.request.method).toBe('POST');
      req.flush(responseMessage);
    });

    it('should trigger NBP fetch with specific date via POST request', () => {
      const date = '2023-10-20';
      const responseMessage = { message: 'Success' };

      service.fetchRatesFromNbp(date).subscribe(res => {
        expect(res).toEqual(responseMessage);
      });

      const req = httpMock.expectOne(`http://localhost:8000/currencies/fetch?date=${date}`);
      expect(req.request.method).toBe('POST');
      req.flush(responseMessage);
    });
  });
});
