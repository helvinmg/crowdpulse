"""API usage log model — tracks every external API call in the database."""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from datetime import datetime
from app.core.database import Base


class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # None = global/shared key
    service = Column(String(50), nullable=False, index=True)
    endpoint = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="success")  # success, blocked, error
    response_time_ms = Column(Float, nullable=True)
    records_fetched = Column(Integer, nullable=True, default=0)
    error_message = Column(Text, nullable=True)
    daily_count = Column(Integer, nullable=True)
    daily_limit = Column(Integer, nullable=True)
    called_at = Column(DateTime, default=datetime.utcnow, index=True)
