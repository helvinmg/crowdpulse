"""Layer 1: X/Twitter scraper using Tweepy (free tier)."""

import tweepy
from datetime import datetime, timezone
from loguru import logger
from app.core.config import get_settings
from app.core.usage_tracker import record_usage, is_blocked

settings = get_settings()

# Search queries for Indian stock market discussions
DEFAULT_QUERIES = [
    "#Nifty50",
    "#IndianStockMarket",
    "#StockMarketIndia",
]


def create_client(bearer_token: str | None = None) -> tweepy.Client:
    token = bearer_token or settings.TWITTER_BEARER_TOKEN
    return tweepy.Client(bearer_token=token)


def fetch_tweets(
    query: str,
    max_results: int = 10,  # Free tier is very limited
    bearer_token: str | None = None,
) -> list[dict]:
    """Search recent tweets matching a query (free-tier constraints)."""
    if is_blocked("twitter"):
        logger.warning(f"Twitter API limit reached — skipping query '{query}'")
        return []

    client = create_client(bearer_token)
    tweets = []

    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["created_at", "author_id", "text"],
        )

        if response.data:
            for tweet in response.data:
                tweets.append(
                    {
                        "source": "twitter",
                        "source_id": f"tw_{tweet.id}",
                        "raw_text": tweet.text,
                        "author": str(tweet.author_id),
                        "posted_at": tweet.created_at or datetime.now(timezone.utc),
                    }
                )

        record_usage("twitter", records_fetched=len(tweets))
        logger.info(f"Fetched {len(tweets)} tweets for query '{query}'")

    except Exception as e:
        record_usage("twitter", error_message=str(e))
        logger.error(f"Error fetching tweets for '{query}': {e}")

    return tweets


def scrape_all_queries(
    queries: list[str] | None = None,
    max_results: int = 10,
    bearer_token: str | None = None,
) -> list[dict]:
    """Scrape tweets for all configured queries."""
    queries = queries or DEFAULT_QUERIES

    if is_blocked("twitter"):
        logger.warning("Twitter API limit reached — skipping all queries")
        return []

    all_tweets = []
    for q in queries:
        if is_blocked("twitter"):
            logger.warning("Twitter API limit reached mid-run — stopping")
            break
        tweets = fetch_tweets(q, max_results, bearer_token)
        all_tweets.extend(tweets)
    return all_tweets
