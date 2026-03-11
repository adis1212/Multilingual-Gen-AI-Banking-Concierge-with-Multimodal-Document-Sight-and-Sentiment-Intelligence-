from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from database.db import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id          = Column(String, primary_key=True)
    session_id  = Column(String, ForeignKey("sessions.id"))
    speaker     = Column(String)          # "customer" | "staff" | "ai"
    channel     = Column(String)          # "A" | "B"
    raw_text    = Column(Text)            # original language
    translated  = Column(Text)            # English translation
    language    = Column(String)
    intent      = Column(String)
    confidence  = Column(Float, default=0.0)
    timestamp   = Column(DateTime(timezone=True), server_default=func.now())