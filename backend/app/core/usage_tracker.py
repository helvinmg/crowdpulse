"""API usage tracker and rate limiter for all external services.

Tracks daily usage per service with hybrid limits:
  - Global limits: shared across all users (YouTube, yfinance, Gemini, and
    Telegram/Twitter when using shared/default API keys)
  - Per-user limits: individual quotas when a user has their own API keys
    (Telegram with own session, Twitter with own bearer token)

Thread-safe via threading.Lock.

Global free-tier limits (daily):
  - Telegram:    200 requests/day (Telethon is generous but we cap it)
  - YouTube:     500 requests/day (scraper, no official API key needed)
  - Twitter/X:    50 requests/day (free tier is very limited)
  - yfinance:    500 requests/day (unofficial, be polite)
  - Gemini:    1500 requests/day (free tier)

Per-user limits (when using own keys):
  - Telegram:    200 requests/day per user
  - Twitter/X:   100 requests/day per user
"""

import json
import threading
from datetime import datetime, timezone, date
from pathlib import Path
from loguru import logger

# ---------------------------------------------------------------------------
# Daily limits — loaded from config/usage_limits.json
# Edit that file to adjust limits for production.
# ---------------------------------------------------------------------------

LIMITS_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "usage_limits.json"

_DEFAULT_GLOBAL = {"telegram": 200, "youtube": 500, "twitter": 50, "yfinance": 500, "gemini": 1500}
_DEFAULT_PER_USER = {"telegram": 200, "twitter": 100}
_DEFAULT_ALWAYS_GLOBAL = {"youtube", "yfinance", "gemini"}


def _load_limits():
    """Load limits from config/usage_limits.json, falling back to defaults."""
    global GLOBAL_LIMITS, PER_USER_LIMITS, ALWAYS_GLOBAL
    if LIMITS_FILE.exists():
        try:
            data = json.loads(LIMITS_FILE.read_text(encoding="utf-8"))
            GLOBAL_LIMITS = data.get("global_limits", _DEFAULT_GLOBAL)
            PER_USER_LIMITS = data.get("per_user_limits", _DEFAULT_PER_USER)
            # Remove _comment keys
            GLOBAL_LIMITS = {k: v for k, v in GLOBAL_LIMITS.items() if not k.startswith("_")}
            PER_USER_LIMITS = {k: v for k, v in PER_USER_LIMITS.items() if not k.startswith("_")}
            ALWAYS_GLOBAL = set(data.get("always_global", list(_DEFAULT_ALWAYS_GLOBAL)))
            logger.info(f"Loaded usage limits from {LIMITS_FILE}")
        except Exception as e:
            logger.warning(f"Could not load {LIMITS_FILE}, using defaults: {e}")
            GLOBAL_LIMITS = _DEFAULT_GLOBAL.copy()
            PER_USER_LIMITS = _DEFAULT_PER_USER.copy()
            ALWAYS_GLOBAL = _DEFAULT_ALWAYS_GLOBAL.copy()
    else:
        GLOBAL_LIMITS = _DEFAULT_GLOBAL.copy()
        PER_USER_LIMITS = _DEFAULT_PER_USER.copy()
        ALWAYS_GLOBAL = _DEFAULT_ALWAYS_GLOBAL.copy()


GLOBAL_LIMITS = {}
PER_USER_LIMITS = {}
ALWAYS_GLOBAL = set()
_load_limits()

# Persistent usage log file
USAGE_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "data"
USAGE_LOG_FILE = USAGE_LOG_DIR / "api_usage.json"

_lock = threading.Lock()
_usage: dict[str, dict] = {}
# Structure: {"2026-02-07": {"telegram": 12, "user:5:telegram": 8, ...}}


def _today() -> str:
    return date.today().isoformat()


def _load_usage():
    """Load usage from disk if available."""
    global _usage
    if USAGE_LOG_FILE.exists():
        try:
            _usage = json.loads(USAGE_LOG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            _usage = {}


def _save_usage():
    """Persist usage to disk."""
    try:
        USAGE_LOG_DIR.mkdir(parents=True, exist_ok=True)
        USAGE_LOG_FILE.write_text(
            json.dumps(_usage, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as e:
        logger.warning(f"Could not save usage log: {e}")


def _ensure_today():
    """Ensure today's entry exists with at least the global service keys."""
    today = _today()
    if today not in _usage:
        _usage[today] = {svc: 0 for svc in GLOBAL_LIMITS}


def _usage_key(service: str, user_id: int | None = None) -> str:
    """Return the tracking key: 'telegram' (global) or 'user:5:telegram' (per-user)."""
    if user_id and service not in ALWAYS_GLOBAL:
        return f"user:{user_id}:{service}"
    return service


def _get_limit(service: str, user_id: int | None = None) -> int:
    """Return the applicable daily limit."""
    if user_id and service not in ALWAYS_GLOBAL and service in PER_USER_LIMITS:
        return PER_USER_LIMITS[service]
    return GLOBAL_LIMITS.get(service, 0)


# Initialize on import
_load_usage()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_usage(service: str, user_id: int | None = None) -> int:
    """Get today's usage count for a service (global or per-user)."""
    with _lock:
        _ensure_today()
        key = _usage_key(service, user_id)
        return _usage[_today()].get(key, 0)


def get_limit(service: str, user_id: int | None = None) -> int:
    """Get the daily limit for a service (global or per-user)."""
    return _get_limit(service, user_id)


def get_remaining(service: str, user_id: int | None = None) -> int:
    """Get remaining calls for today."""
    return max(0, get_limit(service, user_id) - get_usage(service, user_id))


def is_blocked(service: str, user_id: int | None = None) -> bool:
    """Check if a service has exceeded its daily limit."""
    return get_usage(service, user_id) >= get_limit(service, user_id)


def record_usage(
    service: str,
    count: int = 1,
    endpoint: str = None,
    records_fetched: int = 0,
    response_time_ms: float = None,
    error_message: str = None,
    user_id: int | None = None,
) -> bool:
    """Record API usage. Returns True if allowed, False if blocked.

    If user_id is provided and the service supports per-user limits,
    usage is tracked per-user. Otherwise, it's tracked globally.
    """
    with _lock:
        _ensure_today()
        today = _today()
        key = _usage_key(service, user_id)
        limit = _get_limit(service, user_id)
        current = _usage[today].get(key, 0)

        scope = f"user:{user_id}" if user_id and service not in ALWAYS_GLOBAL else "global"

        if current + count > limit:
            logger.warning(
                f"API LIMIT REACHED: {service.upper()} ({scope}) — "
                f"{current}/{limit} used today. Call BLOCKED."
            )
            _save_usage()
            _log_to_db(service, endpoint, "blocked", None, 0, None, current, limit, user_id)
            return False

        _usage[today][key] = current + count
        new_total = current + count

        # Log usage at milestones: 50%, 80%, 90%, and every call after 90%
        pct = new_total / limit * 100 if limit else 0
        if pct >= 90 or (pct >= 80 and (new_total - count) / limit * 100 < 80) or (pct >= 50 and (new_total - count) / limit * 100 < 50):
            logger.warning(
                f"API USAGE: {service.upper()} ({scope}) — "
                f"{new_total}/{limit} ({pct:.0f}%) used today"
            )
        else:
            logger.info(
                f"API call: {service.upper()} ({scope}) — "
                f"{new_total}/{limit} ({pct:.0f}%) used today"
            )

        _save_usage()
        status = "error" if error_message else "success"
        _log_to_db(service, endpoint, status, response_time_ms, records_fetched, error_message, new_total, limit, user_id)
        return True


def _log_to_db(service, endpoint, status, response_time_ms, records_fetched, error_message, daily_count, daily_limit, user_id=None):
    """Persist a usage log entry to the database."""
    try:
        from app.core.database import SessionLocal
        from app.models.api_usage_log import ApiUsageLog
        db = SessionLocal()
        try:
            log = ApiUsageLog(
                service=service,
                endpoint=endpoint,
                status=status,
                response_time_ms=response_time_ms,
                records_fetched=records_fetched or 0,
                error_message=error_message,
                daily_count=daily_count,
                daily_limit=daily_limit,
                user_id=user_id,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.debug(f"Could not log usage to DB: {e}")


def get_all_usage_summary(user_id: int | None = None) -> dict:
    """Get a summary of all services' usage for today.

    Returns global usage for always-global services, and per-user usage
    for Telegram/Twitter if user_id is provided.
    """
    with _lock:
        _ensure_today()
        today = _today()
        summary = {}
        for service in GLOBAL_LIMITS:
            key = _usage_key(service, user_id)
            limit = _get_limit(service, user_id)
            used = _usage[today].get(key, 0)
            scope = "per_user" if user_id and service not in ALWAYS_GLOBAL else "global"
            summary[service] = {
                "used": used,
                "limit": limit,
                "remaining": max(0, limit - used),
                "blocked": used >= limit,
                "percent_used": round(used / limit * 100, 1) if limit else 0,
                "scope": scope,
            }
        summary["date"] = today
        return summary


def reset_usage(service: str | None = None, user_id: int | None = None):
    """Reset usage for a service (or all services). For testing only."""
    with _lock:
        _ensure_today()
        today = _today()
        if service:
            key = _usage_key(service, user_id)
            _usage[today][key] = 0
            logger.info(f"Reset usage for {key}")
        else:
            _usage[today] = {svc: 0 for svc in GLOBAL_LIMITS}
            logger.info("Reset all API usage counters")
        _save_usage()
