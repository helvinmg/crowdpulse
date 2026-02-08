"""Application-wide constants."""

# Nifty 50 stock symbols (NSE)
NIFTY_50_SYMBOLS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
    "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "HCLTECH",
    "SUNPHARMA", "TATAMOTORS", "BAJFINANCE", "WIPRO", "TITAN",
    "ULTRACEMCO", "NESTLEIND", "POWERGRID", "NTPC", "TECHM",
    "TATASTEEL", "M&M", "BAJAJFINSV", "INDUSINDBK", "ONGC",
    "JSWSTEEL", "ADANIENT", "ADANIPORTS", "COALINDIA", "GRASIM",
    "CIPLA", "BPCL", "DRREDDY", "EICHERMOT", "DIVISLAB",
    "SBILIFE", "BRITANNIA", "HEROMOTOCO", "APOLLOHOSP", "TATACONSUM",
    "HINDALCO", "BAJAJ-AUTO", "HDFCLIFE", "LTIM", "SHRIRAMFIN",
]

# Sentiment labels
SENTIMENT_LABELS = ["positive", "negative", "neutral"]

# Velocity time windows (in minutes)
VELOCITY_WINDOWS = [5, 60, 1440]  # 5 min, 1 hour, 1 day

# Confidence score weights
CONFIDENCE_WEIGHTS = {
    "model_certainty": 0.4,
    "data_sufficiency": 0.3,
    "signal_consistency": 0.3,
}

# Ingestion intervals (in seconds)
INGESTION_INTERVAL_TELEGRAM = 900      # 15 minutes
INGESTION_INTERVAL_YOUTUBE = 3600      # 1 hour
INGESTION_INTERVAL_TWITTER = 3600      # 1 hour
INGESTION_INTERVAL_MARKET = 900        # 15 minutes
