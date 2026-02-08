"""Layer 2: Text cleaning, normalisation, emoji handling, tokenisation."""

import re
import emoji
from loguru import logger

# ---------------------------------------------------------------------------
# Company name / alias → ticker mapping for Nifty 50
# Covers: full names, common abbreviations, Hinglish slang, hashtags
# ---------------------------------------------------------------------------
SYMBOL_ALIASES: dict[str, str] = {
    # RELIANCE
    "reliance": "RELIANCE", "ril": "RELIANCE", "jio": "RELIANCE",
    "mukesh": "RELIANCE", "ambani": "RELIANCE",
    # TCS
    "tcs": "TCS", "tata consultancy": "TCS",
    # HDFCBANK
    "hdfc bank": "HDFCBANK", "hdfc": "HDFCBANK", "hdfcbank": "HDFCBANK",
    # INFY
    "infosys": "INFY", "infy": "INFY",
    # ICICIBANK
    "icici bank": "ICICIBANK", "icici": "ICICIBANK",
    # HINDUNILVR
    "hindustan unilever": "HINDUNILVR", "hul": "HINDUNILVR",
    "hindunilvr": "HINDUNILVR",
    # ITC
    "itc": "ITC",
    # SBIN
    "sbi": "SBIN", "state bank": "SBIN", "sbin": "SBIN",
    # BHARTIARTL
    "airtel": "BHARTIARTL", "bharti airtel": "BHARTIARTL",
    "bhartiartl": "BHARTIARTL",
    # KOTAKBANK
    "kotak": "KOTAKBANK", "kotak bank": "KOTAKBANK", "kotak mahindra": "KOTAKBANK",
    # LT
    "larsen": "LT", "l&t": "LT", "larsen toubro": "LT",
    # AXISBANK
    "axis bank": "AXISBANK", "axis": "AXISBANK",
    # ASIANPAINT
    "asian paints": "ASIANPAINT", "asian paint": "ASIANPAINT",
    "asianpaint": "ASIANPAINT",
    # MARUTI
    "maruti": "MARUTI", "maruti suzuki": "MARUTI",
    # HCLTECH
    "hcl tech": "HCLTECH", "hcl": "HCLTECH", "hcltech": "HCLTECH",
    # SUNPHARMA
    "sun pharma": "SUNPHARMA", "sunpharma": "SUNPHARMA",
    # TATAMOTORS
    "tata motors": "TATAMOTORS", "tatamotors": "TATAMOTORS",
    # BAJFINANCE
    "bajaj finance": "BAJFINANCE", "bajfinance": "BAJFINANCE",
    # WIPRO
    "wipro": "WIPRO",
    # TITAN
    "titan": "TITAN",
    # ULTRACEMCO
    "ultratech": "ULTRACEMCO", "ultratech cement": "ULTRACEMCO",
    # NESTLEIND
    "nestle": "NESTLEIND", "nestle india": "NESTLEIND",
    # POWERGRID
    "power grid": "POWERGRID", "powergrid": "POWERGRID",
    # NTPC
    "ntpc": "NTPC",
    # TECHM
    "tech mahindra": "TECHM", "techm": "TECHM",
    # TATASTEEL
    "tata steel": "TATASTEEL", "tatasteel": "TATASTEEL",
    # M&M
    "mahindra": "M&M", "m&m": "M&M", "mahindra mahindra": "M&M",
    # BAJAJFINSV
    "bajaj finserv": "BAJAJFINSV", "bajajfinsv": "BAJAJFINSV",
    # INDUSINDBK
    "indusind": "INDUSINDBK", "indusind bank": "INDUSINDBK",
    # ONGC
    "ongc": "ONGC",
    # JSWSTEEL
    "jsw steel": "JSWSTEEL", "jsw": "JSWSTEEL",
    # ADANIENT
    "adani": "ADANIENT", "adani enterprises": "ADANIENT",
    "adanient": "ADANIENT",
    # ADANIPORTS
    "adani ports": "ADANIPORTS", "adaniports": "ADANIPORTS",
    # COALINDIA
    "coal india": "COALINDIA", "coalindia": "COALINDIA",
    # GRASIM
    "grasim": "GRASIM",
    # CIPLA
    "cipla": "CIPLA",
    # BPCL
    "bpcl": "BPCL", "bharat petroleum": "BPCL",
    # DRREDDY
    "dr reddy": "DRREDDY", "drreddy": "DRREDDY", "dr reddys": "DRREDDY",
    # EICHERMOT
    "eicher": "EICHERMOT", "royal enfield": "EICHERMOT",
    "eicher motors": "EICHERMOT",
    # DIVISLAB
    "divis lab": "DIVISLAB", "divi's": "DIVISLAB", "divislab": "DIVISLAB",
    # SBILIFE
    "sbi life": "SBILIFE", "sbilife": "SBILIFE",
    # BRITANNIA
    "britannia": "BRITANNIA",
    # HEROMOTOCO
    "hero": "HEROMOTOCO", "hero motocorp": "HEROMOTOCO",
    "heromotoco": "HEROMOTOCO",
    # APOLLOHOSP
    "apollo": "APOLLOHOSP", "apollo hospital": "APOLLOHOSP",
    "apollo hospitals": "APOLLOHOSP",
    # TATACONSUM
    "tata consumer": "TATACONSUM", "tataconsum": "TATACONSUM",
    # HINDALCO
    "hindalco": "HINDALCO",
    # BAJAJ-AUTO
    "bajaj auto": "BAJAJ-AUTO", "bajaj-auto": "BAJAJ-AUTO",
    # HDFCLIFE
    "hdfc life": "HDFCLIFE", "hdfclife": "HDFCLIFE",
    # LTIM
    "ltimindtree": "LTIM", "lt mindtree": "LTIM", "ltim": "LTIM",
    "mindtree": "LTIM",
    # SHRIRAMFIN
    "shriram": "SHRIRAMFIN", "shriram finance": "SHRIRAMFIN",
    # Generic market terms → no specific symbol, skip
}


def clean_text(text: str) -> str:
    """Clean and normalise raw social media text for NLP."""
    if not text:
        return ""

    # Convert emojis to text descriptions (e.g. 🚀 -> :rocket:)
    text = emoji.demojize(text, delimiters=(" __", "__ "))

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove mentions (@user)
    text = re.sub(r"@\w+", "", text)

    # Remove hashtag symbols but keep the word
    text = re.sub(r"#(\w+)", r"\1", text)

    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove special characters but keep Devanagari (for Hindi in Hinglish)
    text = re.sub(r"[^\w\s\u0900-\u097F]", " ", text)

    # Collapse whitespace again
    text = re.sub(r"\s+", " ", text).strip()

    return text.lower()


def extract_stock_mentions(text: str, symbols: list[str]) -> list[str]:
    """Extract Nifty 50 stock symbol mentions from text.

    Checks both exact ticker symbols (e.g. RELIANCE, TCS) and common
    company names / aliases (e.g. 'infosys' → INFY, 'airtel' → BHARTIARTL).
    """
    text_upper = text.upper()
    text_lower = text.lower()
    found: set[str] = set()

    # 1. Exact ticker match (word-boundary for short tickers)
    for sym in symbols:
        if len(sym) <= 3:
            if re.search(rf'\b{re.escape(sym)}\b', text_upper):
                found.add(sym)
        else:
            if sym in text_upper:
                found.add(sym)

    # 2. Alias / company name match
    for alias, sym in SYMBOL_ALIASES.items():
        # Use word-boundary check to avoid false positives
        # e.g. "titan" should match but "titanium" ideally shouldn't,
        # however for social media text, substring is acceptable for
        # multi-word aliases; single short words use boundary check.
        if len(alias) <= 3:
            # Short aliases: require word boundary
            if re.search(rf'\b{re.escape(alias)}\b', text_lower):
                found.add(sym)
        else:
            if alias in text_lower:
                found.add(sym)

    return list(found)


def batch_clean(texts: list[str]) -> list[str]:
    """Clean a batch of texts."""
    cleaned = []
    for t in texts:
        try:
            cleaned.append(clean_text(t))
        except Exception as e:
            logger.warning(f"Error cleaning text: {e}")
            cleaned.append("")
    return cleaned
