from datetime import date
from typing import List, Optional

import models
import schemas
from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

app = FastAPI(title="Currency Converter API")

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def fetch_currencies(date: Optional[date] = None, db: Session = Depends(get_db)):
    """
    Pobiera dane z API NBP i zapisuje je do bazy danych.
    Jeśli podano datę, pobiera kursy dla tej daty. W przeciwnym razie pobiera aktualną tabelę.
    """
    from nbp_service import fetch_exchange_rates, normalize_data, save_rates

    raw_data = fetch_exchange_rates(date)
    if not raw_data:
        raise HTTPException(status_code=404, detail="Nie udało się pobrać danych z API NBP (brak danych dla wybranej daty lub błąd połączenia)")

    normalized_data = normalize_data(raw_data)
    added_count = save_rates(db, normalized_data)

    return {
        "message": f"Pomyślnie zsynchronizowano dane. Dodano {added_count} nowych kursów.",
        "tables_fetched": len(raw_data)
    }
