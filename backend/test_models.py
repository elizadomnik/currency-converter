from datetime import date

import pytest
from database import Base
from models import Currency, Rate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestModels:
    @pytest.fixture(scope="function")
    def db_session(self):
        """
        Creates a new database session for each test.
        Creates tables before the test and drops them after.
        """
        Base.metadata.create_all(bind=engine)
        session = TestingSessionLocal()
        yield session
        session.close()
        Base.metadata.drop_all(bind=engine)

    def test_should_create_currency_correctly(self, db_session):
        """
        Test verifying the correct creation of the Currency model.
        """
        # Given: A new currency object
        currency_data = {"code": "USD", "name": "United States Dollar"}
        
        # When: We save the currency to the database
        currency = Currency(**currency_data)
        db_session.add(currency)
        db_session.commit()
        db_session.refresh(currency)

        # Then: The object should be correctly saved with an assigned ID
        assert currency.id is not None
        assert currency.code == "USD"
        assert currency.name == "United States Dollar"

    def test_should_create_rate_linked_to_currency(self, db_session):
        """
        Test verifying the correct creation of a Rate assigned to a Currency.
        """
        # Given: An existing currency in the database
        currency = Currency(code="EUR", name="Euro")
        db_session.add(currency)
        db_session.commit()

        # When: We create a rate for this currency
        rate = Rate(currency_id=currency.id, date=date(2026, 1, 30), rate=4.25)
        db_session.add(rate)
        db_session.commit()
        db_session.refresh(rate)

        # Then: The rate should be correctly saved and linked to the currency ID
        assert rate.id is not None
        assert rate.currency_id == currency.id
        assert rate.rate == 4.25
        assert rate.date == date(2026, 1, 30)

    def test_should_retrieve_rates_via_currency_relationship(self, db_session):
        """
        Test verifying the one-to-many relationship between Currency and Rates.
        """
        # Given: A currency with two assigned rates
        currency = Currency(code="GBP", name="British Pound")
        db_session.add(currency)
        db_session.commit()

        rate1 = Rate(currency_id=currency.id, date=date(2026, 1, 29), rate=5.01)
        rate2 = Rate(currency_id=currency.id, date=date(2026, 1, 30), rate=5.05)
        db_session.add_all([rate1, rate2])
        db_session.commit()

        # When: We retrieve the currency from the database
        db_session.refresh(currency)

        # Then: We should have access to the list of rates via the relationship
        assert len(currency.rates) == 2
        assert currency.rates[0].rate == 5.01
        assert currency.rates[1].rate == 5.05
