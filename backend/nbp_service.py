from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests
from models import Currency, Rate
from sqlalchemy.orm import Session

NBP_API_URL = "https://api.nbp.pl/api/exchangerates/tables/a/"

def fetch_exchange_rates(target_date: Optional[date] = None) -> List[Dict[str, Any]]:
    """
    Pobiera kursy walut z API NBP (Tabela A).

    Args:
        target_date: Opcjonalna data, dla której mają zostać pobrane kursy. Jeśli None, pobiera aktualną tabelę.

    Returns:
        Lista słowników zawierająca dane z NBP lub pusta lista w przypadku błędu.
    """
    url = NBP_API_URL
    if target_date:
        url += f"{target_date.strftime('%Y-%m-%d')}/"

    url += "?format=json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych z NBP: {e}")
        return []

def normalize_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalizuje dane z odpowiedzi API NBP do płaskiej struktury.

    Args:
        data: Surowe dane JSON z API NBP.

    Returns:
        Lista słowników ze znormalizowanymi danymi kursów.
    """
    normalized_rates = []
    if not data:
        return normalized_rates

    for table in data:
        effective_date_str = table.get("effectiveDate")
        if not isinstance(effective_date_str, str):
            continue

        try:
            effective_date = datetime.strptime(effective_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        for item in table.get("rates", []):
            normalized_rates.append({
                "date": effective_date,
                "code": item.get("code"),
                "name": item.get("currency"),
                "rate": item.get("mid")
            })

    return normalized_rates

def save_rates(db: Session, rates_data: List[Dict[str, Any]]) -> int:
    """
    Zapisuje znormalizowane kursy do bazy danych.
    Tworzy walutę (Currency), jeśli nie istnieje.
    Tworzy kurs (Rate), jeśli nie istnieje dla danej daty/waluty.

    Args:
        db: Sesja bazy danych.
        rates_data: Lista słowników ze znormalizowanymi danymi kursów.

    Returns:
        Liczba dodanych nowych kursów.
    """
    added_count = 0

    existing_currencies = {c.code: c for c in db.query(Currency).all()}

    for item in rates_data:
        code = item["code"]
        name = item["name"]
        rate_value = item["rate"]
        rate_date = item["date"]

        currency = existing_currencies.get(code)
        if not currency:
            currency = Currency(code=code, name=name)
            db.add(currency)
            db.flush()
            existing_currencies[code] = currency

        existing_rate = db.query(Rate).filter(
            Rate.currency_id == currency.id,
            Rate.date == rate_date
        ).first()

        if not existing_rate:
            new_rate = Rate(
                currency_id=currency.id,
                date=rate_date,
                rate=rate_value
            )
            db.add(new_rate)
            added_count += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Błąd podczas zapisu do bazy danych: {e}")
        raise e

    return added_count
