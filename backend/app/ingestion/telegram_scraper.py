"""Layer 1: Telegram public channel scraper using Telethon."""

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timezone
from loguru import logger
from app.core.config import get_settings
from app.core.usage_tracker import record_usage, is_blocked

settings = get_settings()

# ---------------------------------------------------------------------------
# Indian stock market Telegram channels (public)
# These are high-activity retail trader channels with Hinglish content.
# ---------------------------------------------------------------------------
DEFAULT_CHANNELS = [
    # Usha's Analysis — Massive retail following (370k+); very active for F&O sentiment
    "UshasAnalysis",
    # Equitymaster — High-density data for Sensex/Nifty sentiment analysis
    "equitymasterofficial",
    # Nifty Stock Trades — Focuses on Nifty levels; rich in Hinglish market slang
    "way2laabh02",
    # Esha Analysis — High intraday engagement; good for "panic/hype" triggers
    "stocknifty09",
    # Stock Market Ninjas — Smaller but high-frequency updates from active retail traders
    "StockMarketNinjas",
]


async def create_client(session_string: str | None = None) -> TelegramClient | None:
    """Create and authenticate a Telegram client.

    Args:
        session_string: If provided, use this StringSession (from user onboarding).
                        Otherwise, fall back to file-based session.

    Returns None if no valid session is available or authentication fails.
    """
    from pathlib import Path
    from telethon.sessions import StringSession

    try:
        if session_string:
            # User-provided session from onboarding
            client = TelegramClient(
                StringSession(session_string),
                int(settings.TELEGRAM_API_ID),
                settings.TELEGRAM_API_HASH,
            )
        else:
            # File-based session (created via create_telegram_session.py)
            session_file = Path(f"{settings.TELEGRAM_SESSION_NAME}.session")
            if not session_file.exists():
                logger.error(
                    f"Telegram session file '{session_file}' not found. "
                    "Run 'python create_telegram_session.py' first to authenticate."
                )
                return None
            client = TelegramClient(
                settings.TELEGRAM_SESSION_NAME,
                int(settings.TELEGRAM_API_ID),
                settings.TELEGRAM_API_HASH,
            )

        await client.connect()

        if not await client.is_user_authorized():
            logger.error(
                "Telegram session expired or not authorized. "
                "Run 'python create_telegram_session.py' to re-authenticate."
            )
            await client.disconnect()
            return None

        logger.info("Telegram client connected successfully")
        return client

    except Exception as e:
        logger.error(f"Failed to create Telegram client: {e}")
        return None


async def fetch_channel_messages(
    client: TelegramClient,
    channel_username: str,
    limit: int = 100,
    min_date: datetime | None = None,
) -> list[dict]:
    """Fetch recent messages from a public Telegram channel."""
    if is_blocked("telegram"):
        logger.warning(f"Telegram API limit reached — skipping @{channel_username}")
        return []

    if not record_usage("telegram"):
        return []

    try:
        entity = await client.get_entity(channel_username)
        history = await client(
            GetHistoryRequest(
                peer=entity,
                limit=limit,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0,
            )
        )

        messages = []
        for msg in history.messages:
            if not msg.message:
                continue
            if min_date and msg.date < min_date:
                continue
            messages.append(
                {
                    "source": "telegram",
                    "source_id": f"tg_{channel_username}_{msg.id}",
                    "raw_text": msg.message,
                    "author": channel_username,
                    "posted_at": msg.date.astimezone(timezone.utc),
                }
            )

        logger.info(f"Fetched {len(messages)} messages from @{channel_username}")
        return messages

    except Exception as e:
        logger.error(f"Error fetching from @{channel_username}: {e}")
        return []


async def scrape_all_channels(
    channels: list[str] | None = None,
    limit: int = 100,
    min_date: datetime | None = None,
    session_string: str | None = None,
) -> list[dict]:
    """Scrape messages from all configured channels."""
    channels = channels or DEFAULT_CHANNELS
    if not channels:
        logger.warning("No Telegram channels configured")
        return []

    if is_blocked("telegram"):
        logger.warning("Telegram API limit reached — skipping all channels")
        return []

    client = await create_client(session_string=session_string)
    if client is None:
        logger.warning("Telegram client unavailable — skipping ingestion")
        return []

    all_messages = []
    try:
        for ch in channels:
            if is_blocked("telegram"):
                logger.warning("Telegram API limit reached mid-run — stopping")
                break
            msgs = await fetch_channel_messages(client, ch, limit, min_date)
            all_messages.extend(msgs)
    finally:
        await client.disconnect()

    return all_messages
