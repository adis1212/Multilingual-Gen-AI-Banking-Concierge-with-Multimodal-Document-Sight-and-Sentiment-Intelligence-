from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from database.db import Base


class Document(Base):
    __tablename__ = "documents"

    id          = Column(String, primary_key=True)
    session_id  = Column(String, ForeignKey("sessions.id"))
    doc_type    = Column(String)          # "aadhaar" | "pan" | "passbook"
    ocr_result  = Column(JSON, default={})
    mismatches  = Column(JSON, default=[])
    is_verified = Column(Boolean, default=False)
    ai_note     = Column(Text)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())