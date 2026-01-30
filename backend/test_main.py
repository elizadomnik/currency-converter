from datetime import date

import models
import pytest
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_read_root():
    """Test endpointu głównego."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Currency Converter API is running"}

def test_get_currencies_empty():
    """Test pobierania listy walut, gdy baza jest pusta."""
    response = client.get("/currencies")
    assert response.status_code == 200
    assert response.json() == []

def test_get_currencies_with_data():
    """Test pobierania listy walut z danymi."""
    db = TestingSessionLocal()
    db.add(models.Currency(code="USD", name="dolar amerykański"))
    db.commit()

    response = client.get("/currencies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "USD"
    db.close()

def test_get_currencies_by_date():
    """Test pobierania kursów walut dla konkretnej daty."""
    db = TestingSessionLocal()
    curr = models.Currency(code="EUR", name="euro")
    db.add(curr)
    db.flush()

    today = date(2026, 1, 30)
    db.add(models.Rate(currency_id=curr.id, date=today, rate=4.25))
    db.add(models.Rate(currency_id=curr.id, date=date(2026, 1, 29), rate=4.20))
    db.commit()

    # Test filtrowania po dacie
    response = client.get("/currencies/2026-01-30")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["rate"] == 4.25
    assert data[0]["currency"]["code"] == "EUR"
    db.close()

def test_fetch_rates_mock(mocker):
    """Test endpointu fetch z mockowanym serwisem NBP."""
    # Mockowanie nbp_service
    mock_fetch = mocker.patch("nbp_service.fetch_exchange_rates")
    mock_fetch.return_value = [{
        "table": "A",
        "no": "001/A/NBP/2026",
        "effectiveDate": "2026-01-30",
        "rates": [{"currency": "testowa", "code": "TST", "mid": 1.23}]
    }]

    response = client.post("/currencies/fetch")
    assert response.status_code == 200
    assert "Pomyślnie zsynchronizowano dane" in response.json()["message"]

    # Weryfikacja zapisu w bazie
    db = TestingSessionLocal()
    currency = db.query(models.Currency).filter_by(code="TST").first()
    assert currency is not None
    rate = db.query(models.Rate).filter_by(currency_id=currency.id).first()
    assert rate is not None
    assert rate.rate == 1.23
    db.close()
