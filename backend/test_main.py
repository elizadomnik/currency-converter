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

client = TestClient(app)

class TestCurrencyAPI:
    @pytest.fixture(autouse=True)
    def setup_db(self):
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)

    def test_should_return_welcome_message_on_root(self):
        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Currency Converter API is running"}

    def test_should_return_empty_list_when_no_currencies(self):
        response = client.get("/currencies")

        assert response.status_code == 200
        assert response.json() == []

    def test_should_return_list_of_currencies(self):
        db = TestingSessionLocal()
        db.add(models.Currency(code="USD", name="United States Dollar"))
        db.commit()

        response = client.get("/currencies")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["code"] == "USD"
        db.close()

    def test_should_return_rates_for_specific_date(self):
        db = TestingSessionLocal()
        curr = models.Currency(code="EUR", name="Euro")
        db.add(curr)
        db.flush()

        today = date(2026, 1, 30)
        db.add(models.Rate(currency_id=curr.id, date=today, rate=4.25))
        db.add(models.Rate(currency_id=curr.id, date=date(2026, 1, 29), rate=4.20))
        db.commit()

        response = client.get("/currencies/2026-01-30")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["rate"] == 4.25
        assert data[0]["currency"]["code"] == "EUR"
        db.close()

    def test_should_fetch_and_store_rates_from_external_api(self, mocker):
        mock_fetch = mocker.patch("nbp_service.fetch_exchange_rates")
        mock_fetch.return_value = [{
            "table": "A",
            "no": "001/A/NBP/2026",
            "effectiveDate": "2026-01-30",
            "rates": [{"currency": "test currency", "code": "TST", "mid": 1.23}]
        }]

        response = client.post("/currencies/fetch")


        assert response.status_code == 200
        assert "successfully synchronized" in response.json()["message"] or "Pomyślnie zsynchronizowano" in response.json()["message"]

        db = TestingSessionLocal()
        currency = db.query(models.Currency).filter_by(code="TST").first()
        assert currency is not None
        rate = db.query(models.Rate).filter_by(currency_id=currency.id).first()
        assert rate is not None
        assert rate.rate == 1.23
        db.close()
