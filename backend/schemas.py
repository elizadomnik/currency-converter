from datetime import date

from pydantic import BaseModel, ConfigDict


class CurrencyBase(BaseModel):
    """
    Podstawowy model waluty.
    """
    code: str
    name: str

class Currency(CurrencyBase):
    """
    Model waluty z identyfikatorem z bazy danych.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)

class RateBase(BaseModel):
    """
    Podstawowy model kursu waluty.
    """
    date: date
    rate: float

class Rate(RateBase):
    """
    Model kursu z identyfikatorem i powiązaniem z walutą.
    """
    id: int
    currency_id: int

    model_config = ConfigDict(from_attributes=True)

class RateWithCurrency(RateBase):
    """
    Model kursu zawierający pełne informacje o walucie.
    """
    currency: CurrencyBase

    model_config = ConfigDict(from_attributes=True)
