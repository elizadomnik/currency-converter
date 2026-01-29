from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    rates = relationship("Rate", back_populates="currency")

class Rate(Base):
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, index=True)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    rate = Column(Float, nullable=False)

    currency = relationship("Currency", back_populates="rates")
