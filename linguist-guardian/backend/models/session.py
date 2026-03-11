from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from database.db import Base


class Session(Base):
    __tablename__ = "sessions"

    id          = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    staff_id    = Column(String)
    branch_id   = Column(String)
    token_number = Column(String)
    status      = Column(String, default="active")   # active / closed
    intent_log  = Column(JSON, default=[])
    sentiment_log = Column(JSON, default=[])
    actions_taken = Column(JSON, default=[])
    summary     = Column(Text)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    closed_at   = Column(DateTime(timezone=True))