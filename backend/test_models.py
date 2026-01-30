from datetime import date

import pytest
from database import Base
from models import Currency, Rate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Tworzy nową sesję bazy danych dla każdego testu.
    Tworzy tabele przed testem i usuwa je po zakończeniu.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_currency(db_session):
    """
    Test tworzenia nowej waluty.
    """
    currency = Currency(code="USD", name="dolar amerykański")
    db_session.add(currency)
    db_session.commit()
    db_session.refresh(currency)

    assert currency.id is not None
    assert currency.code == "USD"
    assert currency.name == "dolar amerykański"

def test_create_rate(db_session):
    """
    Test tworzenia kursu dla waluty.
    """
    currency = Currency(code="EUR", name="euro")
    db_session.add(currency)
    db_session.commit()

    rate = Rate(currency_id=currency.id, date=date(2026, 1, 30), rate=4.25)
    db_session.add(rate)
    db_session.commit()
    db_session.refresh(rate)

    assert rate.id is not None
    assert rate.currency_id == currency.id
    assert rate.rate == 4.25
    assert rate.date == date(2026, 1, 30)

def test_currency_rate_relationship(db_session):
    """
    Test relacji między walutą a kursami.
    """
    currency = Currency(code="GBP", name="funt szterling")
    db_session.add(currency)
    db_session.commit()

    rate1 = Rate(currency_id=currency.id, date=date(2026, 1, 29), rate=5.01)
    rate2 = Rate(currency_id=currency.id, date=date(2026, 1, 30), rate=5.05)
    db_session.add_all([rate1, rate2])
    db_session.commit()

    db_session.refresh(currency)
    assert len(currency.rates) == 2
    assert currency.rates[0].rate == 5.01
    assert currency.rates[1].rate == 5.05
