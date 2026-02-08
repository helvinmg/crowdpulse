"""Onboarding & user config routes: Telegram validation, YouTube/Twitter settings."""

import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.user_config import UserConfig
from loguru import logger

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class TelegramSetup(BaseModel):
    api_id: str
    api_hash: str
    phone: str


class TelegramVerify(BaseModel):
    code: str
    password: str | None = None
    phone_code_hash: str | None = None


class YouTubeSetup(BaseModel):
    video_ids: list[str]


class TwitterSetup(BaseModel):
    queries: list[str]
    bearer_token: str | None = None


class RedditSetup(BaseModel):
    subreddits: list[str]
    client_id: str | None = None
    client_secret: str | None = None


class SkipOnboarding(BaseModel):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_config(db: Session, user_id: int) -> UserConfig:
    config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
    if not config:
        config = UserConfig(user_id=user_id, use_defaults=True)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


# ---------------------------------------------------------------------------
# Telegram: Step 1 — Send OTP code
# ---------------------------------------------------------------------------

# In-memory store for pending Telegram clients (keyed by user_id)
_pending_telegram_clients: dict[int, object] = {}


@router.post("/telegram/send-code")
async def telegram_send_code(
    req: TelegramSetup,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send Telegram OTP code to the user's phone number."""
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
    except ImportError:
        raise HTTPException(status_code=500, detail="Telethon not installed")

    config = _get_or_create_config(db, user.id)

    # Save credentials
    config.telegram_api_id = req.api_id
    config.telegram_api_hash = req.api_hash
    config.telegram_phone = req.phone
    config.telegram_validated = False
    db.commit()

    # Create client with StringSession (no file needed)
    client = TelegramClient(StringSession(), int(req.api_id), req.api_hash)
    await client.connect()

    try:
        result = await client.send_code_request(req.phone)
        # Store client for verification step
        _pending_telegram_clients[user.id] = client
        return {
            "status": "code_sent",
            "phone_code_hash": result.phone_code_hash,
            "message": f"OTP sent to {req.phone}. Enter the code to verify.",
        }
    except Exception as e:
        await client.disconnect()
        logger.error(f"Telegram send_code failed for user {user.id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Telegram: Step 2 — Verify OTP code
# ---------------------------------------------------------------------------

@router.post("/telegram/verify")
async def telegram_verify(
    req: TelegramVerify,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verify the Telegram OTP code and save the session."""
    from telethon.sessions import StringSession
    from telethon.errors import SessionPasswordNeededError

    client = _pending_telegram_clients.get(user.id)
    if not client:
        raise HTTPException(status_code=400, detail="No pending Telegram verification. Send code first.")

    config = _get_or_create_config(db, user.id)

    try:
        await client.sign_in(config.telegram_phone, req.code)
    except SessionPasswordNeededError:
        if req.password:
            # User provided 2FA password — complete sign-in
            try:
                await client.sign_in(password=req.password)
            except Exception as e:
                await client.disconnect()
                _pending_telegram_clients.pop(user.id, None)
                raise HTTPException(status_code=400, detail=f"2FA password incorrect: {e}")
        else:
            # 2FA required but no password provided — tell frontend to ask for it
            return {
                "status": "needs_2fa",
                "message": "Your Telegram account has Two-Step Verification enabled. Please enter your 2FA cloud password.",
            }
    except Exception as e:
        await client.disconnect()
        _pending_telegram_clients.pop(user.id, None)
        raise HTTPException(status_code=400, detail=f"Verification failed: {e}")

    # Save session string
    session_string = client.session.save()
    config.telegram_session_data = session_string
    config.telegram_validated = True
    config.use_defaults = False
    db.commit()

    await client.disconnect()
    _pending_telegram_clients.pop(user.id, None)

    return {"status": "verified", "message": "Telegram connected successfully!"}


# ---------------------------------------------------------------------------
# Telegram: Set custom channels
# ---------------------------------------------------------------------------

@router.post("/telegram/channels")
def set_telegram_channels(
    channels: list[str],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set custom Telegram channels to scrape."""
    config = _get_or_create_config(db, user.id)
    config.telegram_channels = json.dumps(channels)
    db.commit()
    return {"status": "saved", "channels": channels}


# ---------------------------------------------------------------------------
# YouTube: Set custom video IDs
# ---------------------------------------------------------------------------

@router.post("/youtube")
def set_youtube_config(
    req: YouTubeSetup,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set custom YouTube video IDs to scrape comments from."""
    config = _get_or_create_config(db, user.id)
    config.youtube_video_ids = json.dumps(req.video_ids)
    config.use_defaults = False
    db.commit()
    return {"status": "saved", "video_ids": req.video_ids}


# ---------------------------------------------------------------------------
# Twitter: Set custom queries
# ---------------------------------------------------------------------------

@router.post("/twitter")
def set_twitter_config(
    req: TwitterSetup,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set custom Twitter search queries and optionally API credentials."""
    config = _get_or_create_config(db, user.id)
    config.twitter_queries = json.dumps(req.queries)
    if req.bearer_token:
        config.twitter_bearer_token = req.bearer_token
    config.use_defaults = False
    db.commit()
    return {"status": "saved", "queries": req.queries, "has_api_key": bool(req.bearer_token)}


# ---------------------------------------------------------------------------
# Reddit: Set custom subreddits
# ---------------------------------------------------------------------------

@router.post("/reddit")
def set_reddit_config(
    req: RedditSetup,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set custom Reddit subreddits and optionally API credentials."""
    config = _get_or_create_config(db, user.id)
    config.reddit_subreddits = json.dumps(req.subreddits)
    if req.client_id:
        config.reddit_client_id = req.client_id
    if req.client_secret:
        config.reddit_client_secret = req.client_secret
    config.use_defaults = False
    db.commit()
    return {"status": "saved", "subreddits": req.subreddits, "has_api_creds": bool(req.client_id and req.client_secret)}


# ---------------------------------------------------------------------------
# Skip onboarding (use defaults)
# ---------------------------------------------------------------------------

@router.post("/skip")
def skip_onboarding(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Skip onboarding and use hardcoded default channels/queries."""
    config = _get_or_create_config(db, user.id)
    config.use_defaults = True
    user.onboarding_complete = True
    db.commit()
    return {"status": "skipped", "message": "Using default channels. You can change this in settings."}


# ---------------------------------------------------------------------------
# Complete onboarding
# ---------------------------------------------------------------------------

@router.post("/complete")
def complete_onboarding(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark onboarding as complete."""
    user.onboarding_complete = True
    db.commit()
    return {"status": "complete"}


# ---------------------------------------------------------------------------
# Get current config
# ---------------------------------------------------------------------------

@router.get("/config")
def get_config(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the user's current scraping configuration."""
    config = _get_or_create_config(db, user.id)
    return {
        "use_defaults": config.use_defaults,
        "telegram": {
            "validated": config.telegram_validated,
            "phone": config.telegram_phone,
            "channels": json.loads(config.telegram_channels) if config.telegram_channels else [],
        },
        "youtube": {
            "video_ids": json.loads(config.youtube_video_ids) if config.youtube_video_ids else [],
        },
        "twitter": {
            "queries": json.loads(config.twitter_queries) if config.twitter_queries else [],
            "has_own_api_key": bool(config.twitter_bearer_token),
        },
        "reddit": {
            "subreddits": json.loads(config.reddit_subreddits) if config.reddit_subreddits else [],
            "has_own_api_creds": bool(config.reddit_client_id and config.reddit_client_secret),
        },
    }
