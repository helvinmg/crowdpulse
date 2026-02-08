"""Resolve scraping sources: per-user config with fallback to hardcoded defaults."""

import json
from loguru import logger
from app.core.database import SessionLocal
from app.models.user_config import UserConfig
from app.ingestion.telegram_scraper import DEFAULT_CHANNELS
from app.ingestion.youtube_scraper import DEFAULT_VIDEO_IDS
from app.ingestion.twitter_scraper import DEFAULT_QUERIES
from app.ingestion.reddit_scraper import DEFAULT_SUBREDDITS


def get_telegram_channels(user_id: int | None = None) -> list[str]:
    """Return Telegram channels for a user, or defaults."""
    if user_id:
        config = _get_config(user_id)
        if config and config.telegram_channels and not config.use_defaults:
            channels = json.loads(config.telegram_channels)
            if channels:
                logger.info(f"Using {len(channels)} custom Telegram channels for user {user_id}")
                return channels
    return DEFAULT_CHANNELS


def get_telegram_session(user_id: int | None = None) -> str | None:
    """Return the user's Telegram StringSession data, or None to use file-based session."""
    if user_id:
        config = _get_config(user_id)
        if config and config.telegram_session_data and config.telegram_validated:
            return config.telegram_session_data
    return None


def get_youtube_video_ids(user_id: int | None = None) -> list[str]:
    """Return YouTube video IDs for a user, or defaults."""
    if user_id:
        config = _get_config(user_id)
        if config and config.youtube_video_ids and not config.use_defaults:
            ids = json.loads(config.youtube_video_ids)
            if ids:
                logger.info(f"Using {len(ids)} custom YouTube videos for user {user_id}")
                return ids
    return DEFAULT_VIDEO_IDS


def get_twitter_queries(user_id: int | None = None) -> list[str]:
    """Return Twitter queries for a user, or defaults."""
    if user_id:
        config = _get_config(user_id)
        if config and config.twitter_queries and not config.use_defaults:
            queries = json.loads(config.twitter_queries)
            if queries:
                logger.info(f"Using {len(queries)} custom Twitter queries for user {user_id}")
                return queries
    return DEFAULT_QUERIES


def get_reddit_subreddits(user_id: int | None = None) -> list[str]:
    """Return Reddit subreddits for a user, or defaults."""
    if user_id:
        config = _get_config(user_id)
        if config and config.reddit_subreddits and not config.use_defaults:
            subs = json.loads(config.reddit_subreddits)
            if subs:
                logger.info(f"Using {len(subs)} custom Reddit subreddits for user {user_id}")
                return subs
    return DEFAULT_SUBREDDITS


def _get_config(user_id: int) -> UserConfig | None:
    db = SessionLocal()
    try:
        return db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
    finally:
        db.close()
