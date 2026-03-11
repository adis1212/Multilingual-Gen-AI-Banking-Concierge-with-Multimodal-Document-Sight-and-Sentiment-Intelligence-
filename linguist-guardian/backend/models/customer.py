from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.sql import func
from database.db import Base


class Customer(Base):
    __tablename__ = "customers"

    id          = Column(String, primary_key=True)   # CIF number
    name        = Column(String, nullable=False)
    language    = Column(String, default="mr")        # ISO 639-1
    cibil_score = Column(Integer, default=0)
    kyc_status  = Column(String, default="pending")   # full / partial / pending
    account_balance = Column(Float, default=0.0)
    phone       = Column(String)
    email       = Column(String)
    meta        = Column(JSON, default={})
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())