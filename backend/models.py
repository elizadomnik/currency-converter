from sqlalchemy import Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from typing import List
from datetime import date

class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    rates: Mapped[List["Rate"]] = relationship("Rate", back_populates="currency")

class Rate(Base):
    __tablename__ = "rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    currency_id: Mapped[int] = mapped_column(Integer, ForeignKey("currencies.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    rate: Mapped[float] = mapped_column(Float, nullable=False)

    currency: Mapped["Currency"] = relationship("Currency", back_populates="rates")
