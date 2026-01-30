from datetime import datetime

import models
from behave import given, then, when
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup Test DB
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

@given('the database contains a currency "{code}" with name "{name}"')
def step_impl(context, code, name):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    currency = models.Currency(code=code, name=name)
    db.add(currency)
    db.commit()
    db.close()

@given('the database contains a currency "{code}" with rate {rate} for date "{date_str}"')
def step_impl(context, code, rate, date_str):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    currency = db.query(models.Currency).filter_by(code=code).first()
    if not currency:
        currency = models.Currency(code=code, name=code)
        db.add(currency)
        db.flush()

    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    rate_obj = models.Rate(currency_id=currency.id, date=date_obj, rate=float(rate))
    db.add(rate_obj)
    db.commit()
    db.close()

@when('I request the list of currencies')
def step_impl(context):
    context.response = client.get("/currencies")

@when('I request the rate for "{code}" on "{date_str}"')
def step_impl(context, code, date_str):
    context.response = client.get(f"/currencies/{date_str}")
    context.target_code = code

@then('I should receive a list containing "{code}"')
def step_impl(context, code):
    assert context.response.status_code == 200
    data = context.response.json()
    assert any(item['code'] == code for item in data)

@then('I should receive the rate {rate}')
def step_impl(context, rate):
    assert context.response.status_code == 200
    data = context.response.json()
    found = False
    for item in data:
        if item['currency']['code'] == context.target_code:
            assert float(item['rate']) == float(rate)
            found = True
            break
    assert found, f"Rate for {context.target_code} not found in response"
