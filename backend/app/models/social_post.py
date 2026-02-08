from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(20), nullable=False, index=True)  # telegram, youtube, twitter
    symbol = Column(String(30), nullable=True, index=True)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    source_id = Column(String(255), nullable=True, unique=True)  # dedup key
    posted_at = Column(DateTime(timezone=True), nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(10), nullable=False, default="test", index=True)  # test or live
