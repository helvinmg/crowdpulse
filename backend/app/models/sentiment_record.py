from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from app.core.database import Base


class SentimentRecord(Base):
    __tablename__ = "sentiment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False, index=True)
    symbol = Column(String(30), nullable=True, index=True)
    label = Column(String(10), nullable=False)  # positive, negative, neutral
    score = Column(Float, nullable=False)  # model confidence 0-1
    model_version = Column(String(50), nullable=True)
    scored_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(10), nullable=False, default="test", index=True)  # test or live
