"""Layer 1: Reddit scraper using PRAW for Indian stock market subreddits."""

import praw
from datetime import datetime, timezone
from loguru import logger
from app.core.config import get_settings
from app.core.usage_tracker import record_usage, is_blocked

settings = get_settings()

# ---------------------------------------------------------------------------
# Default subreddits for Indian stock market discussion (heavy Hinglish)
# ---------------------------------------------------------------------------
DEFAULT_SUBREDDITS = [
    "IndianStreetBets",
    "IndianStockMarket",
    "DalalStreetTalks",
]


def create_client() -> praw.Reddit | None:
    """Create a Reddit client using OAuth credentials."""
    client_id = settings.REDDIT_CLIENT_ID
    client_secret = settings.REDDIT_CLIENT_SECRET

    if not client_id or not client_secret:
        logger.warning("Reddit credentials not configured — skipping")
        return None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="CrowdPulse/1.0 (Indian Stock Market Sentiment Analyzer)",
        )
        # Test connection (read-only)
        reddit.read_only = True
        return reddit
    except Exception as e:
        logger.error(f"Failed to create Reddit client: {e}")
        return None


def fetch_subreddit_posts(
    reddit: praw.Reddit,
    subreddit_name: str,
    max_posts: int = 50,
    time_filter: str = "day",
) -> list[dict]:
    """Fetch hot/new posts + top comments from a subreddit."""
    if is_blocked("reddit"):
        logger.warning(f"Reddit API limit reached — skipping r/{subreddit_name}")
        return []

    posts = []

    try:
        subreddit = reddit.subreddit(subreddit_name)

        for submission in subreddit.hot(limit=max_posts):
            if is_blocked("reddit"):
                break

            # Add the post title + selftext
            text = submission.title
            if submission.selftext:
                text += " " + submission.selftext

            posts.append({
                "source": "reddit",
                "source_id": f"reddit_{submission.id}",
                "raw_text": text,
                "author": str(submission.author) if submission.author else "deleted",
                "posted_at": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
            })

            # Fetch top-level comments (most valuable for sentiment)
            submission.comments.replace_more(limit=0)
            for comment in submission.comments[:10]:
                if not comment.body or comment.body == "[deleted]":
                    continue
                posts.append({
                    "source": "reddit",
                    "source_id": f"reddit_{comment.id}",
                    "raw_text": comment.body,
                    "author": str(comment.author) if comment.author else "deleted",
                    "posted_at": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
                })

        record_usage("reddit", records_fetched=len(posts))
        logger.info(f"Fetched {len(posts)} posts/comments from r/{subreddit_name}")

    except Exception as e:
        record_usage("reddit", error_message=str(e))
        logger.error(f"Error fetching from r/{subreddit_name}: {e}")

    return posts


def scrape_all_subreddits(
    subreddits: list[str] | None = None,
    max_posts: int = 50,
) -> list[dict]:
    """Scrape posts from all configured subreddits."""
    subreddits = subreddits or DEFAULT_SUBREDDITS
    if not subreddits:
        logger.warning("No Reddit subreddits configured")
        return []

    if is_blocked("reddit"):
        logger.warning("Reddit API limit reached — skipping all subreddits")
        return []

    reddit = create_client()
    if reddit is None:
        logger.warning("Reddit client unavailable — skipping ingestion")
        return []

    all_posts = []
    for sub in subreddits:
        if is_blocked("reddit"):
            logger.warning("Reddit API limit reached mid-run — stopping")
            break
        posts = fetch_subreddit_posts(reddit, sub, max_posts)
        all_posts.extend(posts)

    return all_posts
