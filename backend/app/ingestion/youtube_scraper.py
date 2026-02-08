"""Layer 1: YouTube comment scraper using youtube-comment-downloader."""

from youtube_comment_downloader import YoutubeCommentDownloader
from datetime import datetime, timezone
from loguru import logger
from app.core.usage_tracker import record_usage, is_blocked

# ---------------------------------------------------------------------------
# Indian stock market finfluencer channels
# The scraper fetches comments from specific video IDs.
# To find video IDs: go to a video → copy the ?v=XXXXXXXXXXX part from the URL.
# Refresh these periodically with latest uploads from each channel.
# ---------------------------------------------------------------------------
YOUTUBE_CHANNELS = {
    # CA Rachana Ranade — "Stocks to Watch" & "Market Café" videos
    "ca_rachana_ranade": {
        "handle": "@ca_rachana_ranade",
        "search_keywords": ["stocks to watch", "market cafe"],
    },
    # Pranjal Kamra — Sector deep-dives (high comment volume)
    "PranjalKamra": {
        "handle": "@PranjalKamra",
        "search_keywords": ["sector analysis", "stock market"],
    },
    # Ghanshyam Tech — Daily Bank Nifty analysis (intense retail slang)
    "GhanshyamTech": {
        "handle": "@GhanshyamTech",
        "search_keywords": ["bank nifty", "nifty analysis"],
    },
    # Asset Yogi — Market news wrap-ups
    "AssetYogi": {
        "handle": "@AssetYogi",
        "search_keywords": ["market news", "stock market"],
    },
    # Pushkar Raj Thakur — High-energy "momentum" videos (emotional comments)
    "PushkarRajThakur": {
        "handle": "@PushkarRajThakur",
        "search_keywords": ["momentum", "stock market"],
    },
}

# Add specific video IDs here once you find high-comment videos from the channels above.
# Format: just the video ID part from the URL (e.g. "dQw4w9WgXcQ")
DEFAULT_VIDEO_IDS: list[str] = [
    # CA Rachana Ranade
    "2zEnoW8p130",
    # Pranjal Kamra
    "OikHhpb0Q1M",
    # Ghanshyam Tech
    "ZNCUHPYuDGY",
    # Asset Yogi
    "v2c0tbDxZhg",
    # Pushkar Raj Thakur
    "CINfSuCboqY",
]


def fetch_video_comments(video_id: str, max_comments: int = 200) -> list[dict]:
    """Fetch comments from a single YouTube video."""
    if is_blocked("youtube"):
        logger.warning(f"YouTube API limit reached — skipping video {video_id}")
        return []

    downloader = YoutubeCommentDownloader()
    comments = []

    try:
        for i, comment in enumerate(downloader.get_comments_from_url(
            f"https://www.youtube.com/watch?v={video_id}"
        )):
            if i >= max_comments:
                break
            comments.append(
                {
                    "source": "youtube",
                    "source_id": f"yt_{video_id}_{comment.get('cid', i)}",
                    "raw_text": comment.get("text", ""),
                    "author": comment.get("author", ""),
                    "posted_at": datetime.now(timezone.utc),  # YT comments lack precise timestamps
                }
            )

        record_usage("youtube", records_fetched=len(comments))
        logger.info(f"Fetched {len(comments)} comments from video {video_id}")

    except Exception as e:
        record_usage("youtube", error_message=str(e))
        logger.error(f"Error fetching comments for video {video_id}: {e}")

    return comments


def scrape_all_videos(
    video_ids: list[str] | None = None,
    max_comments: int = 200,
) -> list[dict]:
    """Scrape comments from all configured videos."""
    video_ids = video_ids or DEFAULT_VIDEO_IDS
    if not video_ids:
        logger.warning("No YouTube video IDs configured")
        return []

    if is_blocked("youtube"):
        logger.warning("YouTube API limit reached — skipping all videos")
        return []

    all_comments = []
    for vid in video_ids:
        if is_blocked("youtube"):
            logger.warning("YouTube API limit reached mid-run — stopping")
            break
        comments = fetch_video_comments(vid, max_comments)
        all_comments.extend(comments)

    return all_comments
