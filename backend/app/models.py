from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500), nullable=False, unique=True)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, default="general")
    tags = Column(Text, nullable=False, default="[]")
    source = Column(String(255), nullable=False, default="manual")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    question_logs = relationship("QuestionLog", back_populates="matched_faq")


class QuestionLog(Base):
    __tablename__ = "question_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(String(50), nullable=False)
    input_mode = Column(String(20), nullable=False, default="text")
    matched_confidence = Column(Float, nullable=False, default=0.0)
    fallback_used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    matched_faq_id = Column(Integer, ForeignKey("faqs.id"), nullable=True)
    matched_faq = relationship("FAQ", back_populates="question_logs")
