import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CurrencyDashboardComponent } from './currency-dashboard.component';

describe('CurrencyDashboardComponent', () => {
  let component: CurrencyDashboardComponent;
  let fixture: ComponentFixture<CurrencyDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CurrencyDashboardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CurrencyDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
