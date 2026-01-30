from datetime import date
from typing import List

import models
import schemas
from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

app = FastAPI(title="Currency Converter API")

@app.get("/")
def read_root():
    return {"message": "Currency Converter API is running"}

@app.get("/currencies", response_model=List[schemas.Currency])
def get_currencies(db: Session = Depends(get_db)):
    """
    Zwraca listę dostępnych walut.
    """
    currencies = db.query(models.Currency).all()
    return currencies

@app.get("/currencies/{date}", response_model=List[schemas.RateWithCurrency])
def get_currencies_by_date(date: date, db: Session = Depends(get_db)):
    """
    Zwraca kursy walut z wybranej daty.
    """
    rates = db.query(models.Rate).filter(models.Rate.date == date).all()
    return rates

@app.post("/currencies/fetch")
def fetch_currencies(db: Session = Depends(get_db)):
    """
    Pobiera dane z API NBP i zapisuje je do bazy danych.
    """
    from nbp_service import fetch_exchange_rates, normalize_data, save_rates

    # Pobieranie danych z NBP
    raw_data = fetch_exchange_rates()
    if not raw_data:
        raise HTTPException(status_code=503, detail="Nie udało się pobrać danych z API NBP")

    # Normalizacja i zapis
    normalized_data = normalize_data(raw_data)
    added_count = save_rates(db, normalized_data)

    return {
        "message": f"Pomyślnie zsynchronizowano dane. Dodano {added_count} nowych kursów.",
        "tables_fetched": len(raw_data)
    }
