"""Per-user scraping configuration model."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class UserConfig(Base):
    __tablename__ = "user_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Telegram settings
    telegram_api_id = Column(String(50), nullable=True)
    telegram_api_hash = Column(String(255), nullable=True)
    telegram_phone = Column(String(20), nullable=True)
    telegram_session_data = Column(Text, nullable=True)  # serialised session
    telegram_validated = Column(Boolean, default=False)
    telegram_channels = Column(Text, nullable=True)  # JSON list of channel usernames

    # YouTube settings
    youtube_video_ids = Column(Text, nullable=True)  # JSON list of video IDs

    # Twitter settings
    twitter_queries = Column(Text, nullable=True)  # JSON list of search queries
    twitter_bearer_token = Column(String(255), nullable=True)  # User's own API key

    # Reddit settings
    reddit_subreddits = Column(Text, nullable=True)  # JSON list of subreddit names
    reddit_client_id = Column(String(100), nullable=True)  # User's own API credentials
    reddit_client_secret = Column(String(255), nullable=True)

    # Whether user chose to use defaults
    use_defaults = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
