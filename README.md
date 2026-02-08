# Crowd Pulse

**Near real-time Hinglish sentiment analysis and contrarian signals for the Indian equity market (Nifty 50)**

CrowdPulse scrapes social media chatter (Telegram, YouTube, X/Twitter, Reddit), runs FinBERT-based sentiment analysis on Hinglish text, computes divergence signals by comparing discussion volume against delivery volume, and surfaces contrarian opportunities on a live dashboard.

## Project Structure

```
CrowdPulse/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_auth.py        # /auth/* — signup, login, JWT
│   │   │   ├── routes_onboarding.py  # /onboarding/* — Telegram OTP, YouTube, Twitter, Reddit config
│   │   │   ├── routes_sentiment.py   # /sentiment/* endpoints
│   │   │   ├── routes_divergence.py  # /divergence/* endpoints (incl. index-summary)
│   │   │   ├── routes_market.py      # /market/* endpoints
│   │   │   └── routes_pipeline.py    # /pipeline/run — SSE progress streaming
│   │   ├── core/
│   │   │   ├── auth.py               # Password hashing (bcrypt), JWT tokens, get_current_user
│   │   │   ├── config.py             # Pydantic settings (DB, Redis, API keys, JWT)
│   │   │   ├── constants.py          # Nifty 50 symbols, velocity windows, confidence weights
│   │   │   ├── database.py           # SQLAlchemy engine + session (PostgreSQL / MySQL)
│   │   │   ├── usage_tracker.py      # Per-service daily API usage tracking & rate limiting
│   │   │   └── user_sources.py       # Per-user scraping config with fallback to defaults
│   │   ├── ingestion/
│   │   │   ├── telegram_scraper.py   # Telethon-based channel scraper
│   │   │   ├── youtube_scraper.py    # youtube-comment-downloader scraper
│   │   │   ├── twitter_scraper.py    # Tweepy-based tweet scraper
│   │   │   ├── reddit_scraper.py     # PRAW-based subreddit scraper
│   │   │   └── market_data.py        # yfinance OHLCV + delivery volume fetcher
│   │   ├── nlp/
│   │   │   ├── preprocessor.py       # Text cleaning, emoji→text, Devanagari support
│   │   │   ├── sentiment.py          # FinBERT inference (base or LoRA fine-tuned)
│   │   │   ├── velocity.py           # Rolling-window sentiment velocity (0-100)
│   │   │   ├── labeler_llm.py        # Google Gemini labeling (free tier)
│   │   │   ├── labeler_zeroshot.py   # Zero-shot FinBERT labeling (fallback)
│   │   │   └── finetune.py           # LoRA fine-tuning script for FinBERT
│   │   ├── engine/
│   │   │   ├── divergence.py         # Z-score divergence (discussion vol vs delivery vol)
│   │   │   └── confidence.py         # Weighted confidence (model certainty + data sufficiency + consistency)
│   │   ├── models/
│   │   │   ├── social_post.py        # SocialPost ORM (source, symbol, raw/cleaned text, data_source)
│   │   │   ├── sentiment_record.py   # SentimentRecord ORM (label, score, model_version)
│   │   │   ├── market_data.py        # MarketData ORM (OHLCV + delivery volume/pct)
│   │   │   ├── divergence_signal.py  # DivergenceSignal ORM (divergence, velocity, confidence)
│   │   │   ├── api_usage_log.py      # ApiUsageLog ORM (per-call tracking to DB)
│   │   │   ├── user.py               # User ORM (email, hashed_password, onboarding_complete)
│   │   │   └── user_config.py        # UserConfig ORM (per-user Telegram/YouTube/Twitter/Reddit settings)
│   │   ├── workers/
│   │   │   ├── celery_app.py         # Celery config + beat schedule (optional)
│   │   │   └── tasks.py              # Pipeline tasks (work with or without Celery)
│   │   ├── main.py                   # FastAPI app entry point, CORS, data mode toggle
│   │   ├── pipeline.py               # CLI orchestrator (run pipeline without Celery/Redis)
│   │   └── seed.py                   # 7-day sample data seeder (~14,000 Hinglish posts)
│   ├── create_telegram_session.py    # One-time Telegram auth script (phone + OTP)
│   ├── alembic/                      # DB migrations
│   ├── config/
│   │   └── usage_limits.json         # Editable daily API limits (global + per-user)
│   ├── data/                         # API usage logs (auto-created)
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.jsx              # Main dashboard (stock selector, charts, fetch button)
│   │   │   ├── login/page.jsx        # Login / Signup page
│   │   │   ├── onboarding/page.jsx   # Source setup wizard (Telegram, YouTube, Twitter, Reddit)
│   │   │   ├── settings/page.jsx     # Edit scraping sources after onboarding
│   │   │   ├── overview/page.jsx     # Nifty 50 index overview (pie charts, top movers, table)
│   │   │   ├── usage/page.jsx        # API usage dashboard (progress bars, call logs)
│   │   │   ├── layout.jsx            # Root layout
│   │   │   ├── providers.jsx         # Client-side providers (AuthProvider)
│   │   │   └── globals.css           # CSS variables, dark theme
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   │   ├── SentimentScoreChart.jsx
│   │   │   │   ├── SentimentVelocityChart.jsx
│   │   │   │   └── DivergenceChart.jsx
│   │   │   ├── ApiLimitBanner.jsx    # Warns when free-tier limits are near
│   │   │   ├── ConfidenceCard.jsx    # Per-stock confidence breakdown
│   │   │   ├── DataModeToggle.jsx    # Switch between Test / Live data
│   │   │   ├── DateFilter.jsx        # Preset + custom date range picker
│   │   │   ├── DisclaimerBanner.jsx  # Educational use disclaimer
│   │   │   ├── FetchButton.jsx       # Triggers pipeline via SSE with progress bar
│   │   │   ├── Header.jsx            # App title
│   │   │   ├── OverviewTable.jsx     # Stock overview table
│   │   │   ├── StatsBar.jsx          # Post counts, sources, symbols tracked
│   │   │   ├── StockSelector.jsx     # Nifty 50 stock dropdown
│   │   │   └── AuthGuard.jsx         # Redirects unauthenticated users to /login
│   │   └── lib/
│   │       ├── api.js                # API client (fetch wrappers + SSE pipeline runner)
│   │       ├── auth.js               # AuthContext, login/signup/logout, JWT localStorage
│   │       └── utils.js              # cn(), formatNumber(), directionColor(), confidenceLabel()
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env.example
├── PRODUCT_SPEC.md
├── .gitignore
└── README.md
```

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows (use source venv/bin/activate on Linux/Mac)
pip install -r requirements.txt
cp .env.example .env         # Fill in your API keys
```

### 2. Database Setup

Supports **PostgreSQL** or **MySQL** — set `DATABASE_URL` in `.env`:

```bash
# PostgreSQL (default):
DATABASE_URL=postgresql://postgres:password@localhost:5432/crowdpulse

# MySQL:
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/crowdpulse
```

Redis is **optional** — only needed for Celery scheduled pipeline.

```bash
# Initialize tables (auto-creates all 5 tables)
python -m app.pipeline --init-db

# Or use Alembic for migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 3. Seed Test Data (no live APIs needed)

```bash
python -m app.pipeline --seed
```

Creates **7 days** of realistic Hinglish data for all **50 Nifty stocks**:
- ~14,000 social posts (Telegram, YouTube, Twitter)
- ~14,000 pre-scored sentiment records
- 350 market data rows (OHLCV + delivery volume)
- 2,100 divergence signals (every 4 hours per symbol)

### 4. Run the Pipeline (CLI)

```bash
# Full pipeline: ingest → market → score → signals
python -m app.pipeline --all

# Or run individual steps:
python -m app.pipeline --ingest       # Fetch from Telegram/YouTube/X
python -m app.pipeline --market       # Fetch Nifty 50 market data via yfinance
python -m app.pipeline --score        # Score unprocessed posts with FinBERT
python -m app.pipeline --signals      # Compute divergence + velocity + confidence

# Monitoring:
python -m app.pipeline --status       # Row counts for all tables
python -m app.pipeline --usage        # Today's API usage per service
```

### 5. Start the API

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 6. Celery (scheduled pipeline — production, optional)

```bash
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

Beat schedule:
- Telegram + market data: every **15 min**
- YouTube + Twitter: every **1 hour**
- Signal computation: every **15 min**

### 7. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev
```

Dashboard at http://localhost:3000

## Authentication & Onboarding

The app requires user signup/login before accessing the dashboard.

### Auth Flow
1. **Signup** → `POST /api/v1/auth/signup` (email + password + optional name)
2. **Login** → `POST /api/v1/auth/login` → returns JWT token (valid 72 hours)
3. All protected endpoints require `Authorization: Bearer <token>` header

### Onboarding Flow (after first signup)
New users are redirected to a 3-step setup wizard:

| Step | Action | Skip? |
|------|--------|-------|
| **1. Telegram** | Enter API ID + Hash + phone → OTP verification → save session | Yes |
| **2. YouTube** | Add video IDs to scrape comments from | Yes |
| **3. Twitter** | Add hashtags / search queries to track | Yes |

- **Skip all** → uses hardcoded default channels (5 Telegram channels, 5 YouTube videos, 3 Twitter queries)
- Settings can be changed anytime at `/settings`
- Per-user config stored in `user_configs` table with fallback to defaults

## Data Mode System

The app has two data modes, toggled from the dashboard or via API:

| Mode | Description |
|------|-------------|
| **Test** (default) | Uses seeded sample data. No external API calls. Safe for development. |
| **Live** | Calls real scrapers (Telegram, YouTube, X, yfinance). Requires API keys in `.env`. |

- Toggle via dashboard: click the **Test / Live** toggle button
- Toggle via API: `POST /api/v1/data-mode?mode=live`
- All DB tables have a `data_source` column (`test` or `live`) to keep data isolated

## API Usage Tracking & Free-Tier Limits

Every external API call is tracked with daily limits to stay within free tiers:

| Service | Daily Limit | Notes |
|---------|-------------|-------|
| Telegram | 200 | Telethon (generous, self-capped) |
| YouTube | 500 | Scraper, no API key needed |
| Twitter/X | 50 | Free tier is very limited |
| yfinance | 500 | Unofficial, polite cap |
| Gemini | 1,500 | Free tier for labeling |

- Usage is persisted to `backend/data/api_usage.json` and the `api_usage_logs` DB table
- Calls are **blocked** (not just logged) when limits are exceeded
- View usage: dashboard `/usage` page, `GET /api/v1/usage`, or `python -m app.pipeline --usage`

## Pipeline Architecture

```
Layer 1: Ingestion     Telegram → YouTube → X/Twitter → yfinance
            ↓
Layer 2: Transform     Clean text, emoji→text, URL/mention removal, Devanagari support
            ↓
Layer 3: NLP           FinBERT sentiment scoring (batch, LoRA fine-tuned if available)
                       + rolling-window velocity computation (5m / 60m / 1440m)
            ↓
Layer 4: Engine        Divergence: z-score(discussion_vol) - z-score(delivery_vol)
                       Confidence: 0.4×model_certainty + 0.3×data_sufficiency + 0.3×signal_consistency
            ↓
Layer 5: Storage       PostgreSQL or MySQL
                       Tables: social_posts, sentiment_records, market_data,
                               divergence_signals, api_usage_logs, users, user_configs
            ↓
Layer 6: Dashboard     Next.js 14 + Recharts
                       Pages: /login, /onboarding, / (dashboard), /overview, /usage, /settings
                       Features: JWT auth, onboarding wizard, SSE pipeline, date filter, test/live toggle
```

## API Endpoints

### Sentiment

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/sentiment/latest/{symbol}` | Aggregated sentiment (positive/negative/neutral counts + avg confidence) |
| `GET /api/v1/sentiment/timeseries/{symbol}` | Sentiment score timeseries for charting |
| `GET /api/v1/sentiment/volume/{symbol}` | Hourly discussion volume (post count) |

All sentiment endpoints accept `?hours=`, `?start=`, `?end=`, and `?mode=` query params.

### Divergence & Signals

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/divergence/latest/{symbol}` | Latest divergence signal for a symbol |
| `GET /api/v1/divergence/timeseries/{symbol}` | Divergence signal timeseries |
| `GET /api/v1/divergence/overview` | Latest signal for all Nifty 50 stocks |
| `GET /api/v1/divergence/index-summary` | Nifty 50 index-level analytics (direction/sentiment distribution, top movers, index timeseries) |

### Market

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/market/price/{symbol}` | OHLCV + delivery volume/pct data |

### Authentication

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/signup` | Create account (email, password, name) → JWT token |
| `POST /api/v1/auth/login` | Login → JWT token |
| `GET /api/v1/auth/me` | Get current user (requires Bearer token) |

### Onboarding & Config

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/onboarding/telegram/send-code` | Send Telegram OTP (requires API ID, hash, phone) |
| `POST /api/v1/onboarding/telegram/verify` | Verify OTP → saves session |
| `POST /api/v1/onboarding/telegram/channels` | Set custom Telegram channels |
| `POST /api/v1/onboarding/youtube` | Set custom YouTube video IDs |
| `POST /api/v1/onboarding/twitter` | Set custom Twitter queries |
| `POST /api/v1/onboarding/reddit` | Set custom Reddit subreddits |
| `POST /api/v1/onboarding/skip` | Skip onboarding → use defaults |
| `POST /api/v1/onboarding/complete` | Mark onboarding done |
| `GET /api/v1/onboarding/config` | Get user's current source config |

### Pipeline & System

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/pipeline/run` | Run full pipeline with **SSE progress streaming** |
| `GET /api/v1/status` | Pipeline table row counts |
| `GET /api/v1/stats` | Detailed record stats (by source, unique authors, symbols tracked) |
| `GET /api/v1/data-mode` | Get current data mode (test/live) |
| `POST /api/v1/data-mode?mode=` | Switch data mode |
| `POST /api/v1/seed` | Seed sample data (test mode only) |
| `GET /api/v1/usage` | Today's API usage summary per service |
| `GET /api/v1/usage/logs?limit=` | Recent API call log entries from DB |
| `GET /health` | Health check |

## Database Models

| Table | Key Columns |
|-------|-------------|
| `social_posts` | source, symbol, raw_text, cleaned_text, author, source_id (dedup), posted_at, data_source |
| `sentiment_records` | post_id (FK), symbol, label, score, model_version, scored_at, data_source |
| `market_data` | symbol, date, open/high/low/close, volume, delivery_volume, delivery_pct, data_source |
| `divergence_signals` | symbol, divergence_score, divergence_direction (hype/panic/neutral), sentiment_velocity, confidence_score, model_certainty, data_sufficiency, signal_consistency, data_source |
| `api_usage_logs` | service, endpoint, status (success/blocked/error), response_time_ms, records_fetched, daily_count, daily_limit |
| `users` | email (unique), hashed_password, name, is_active, onboarding_complete |
| `user_configs` | user_id (FK), telegram_api_id/hash/phone/session_data/validated, telegram_channels (JSON), youtube_video_ids (JSON), twitter_queries (JSON), use_defaults |

## Labeling & Fine-Tuning

### Gemini-based labeling (primary — free, get key at https://aistudio.google.com/apikey)

```bash
# From DB
python -m app.nlp.labeler_llm --source db --output data/labeled_llm.jsonl --limit 500

# From file (one comment per line)
python -m app.nlp.labeler_llm --source file --input data/raw_comments.txt --output data/labeled_llm.jsonl
```

### Zero-shot FinBERT labeling (free fallback)

```bash
python -m app.nlp.labeler_zeroshot --source db --output data/labeled_zeroshot.jsonl --limit 1000
```

### Fine-tune FinBERT with LoRA

```bash
python -m app.nlp.finetune --data data/labeled_llm.jsonl data/labeled_zeroshot.jsonl --epochs 3
```

Fine-tuned model saved to `models/finbert-hinglish/` and auto-loaded by the sentiment pipeline.

## Frontend Pages

### `/` — Stock Dashboard
- **Stock selector** dropdown (all Nifty 50 symbols)
- **Sentiment score chart** (timeseries line chart)
- **Sentiment velocity chart** (area chart, 0-100 scale)
- **Divergence chart** (divergence score + confidence over time)
- **Confidence card** (model certainty, data sufficiency, signal consistency breakdown)
- **Fetch button** with SSE progress bar (triggers pipeline from UI)
- **Date range filter** (Today, 3 Days, 7 Days, or custom range)
- **Data mode toggle** (Test / Live)
- **Stats bar** (total posts, sources breakdown, symbols tracked)
- **API limit banner** (warns when approaching free-tier limits)

### `/overview` — Nifty 50 Index Overview
- Index-level stat cards (stocks tracked, avg divergence, avg velocity, total volume, avg confidence)
- Signal direction pie chart (hype / panic / neutral distribution)
- Sentiment distribution pie chart (positive / negative / neutral)
- Index divergence area chart (average divergence over time)
- Volume & velocity bar chart
- Top 5 hype signals and top 5 panic signals tables
- Full Nifty 50 overview table (clickable rows → navigate to stock dashboard)

### `/usage` — API Usage Dashboard
- Per-service usage progress bars with daily limits
- Color-coded status (green → amber → red/blocked)
- Scrollable API call log table (time, service, status, endpoint, records fetched, response time, daily usage)

### `/login` — Login / Signup
- Toggle between login and signup forms
- Email + password authentication
- Auto-redirects to `/onboarding` for new users, `/` for returning users

### `/onboarding` — Source Setup Wizard
- 3-step wizard: Telegram → YouTube → Twitter
- Telegram: API credentials + OTP verification + custom channels
- YouTube: Add video IDs to scrape
- Twitter: Add search queries / hashtags
- Skip individual steps or skip all (uses hardcoded defaults)
- Progress bar showing completion

### `/settings` — Edit Sources
- View and update Telegram channels, YouTube video IDs, Twitter queries
- Per-section save buttons
- Shows Telegram connection status

## Tech Stack

| Layer | Tech |
|-------|------|
| API | FastAPI 0.115, Pydantic v2, Uvicorn |
| Auth | bcrypt, python-jose (JWT), HTTPBearer |
| Task Queue | Celery 5.4 + Redis 5.1 (optional) |
| NLP | FinBERT (ProsusAI/finbert) + LoRA (PEFT 0.13), SpaCy 3.8, NLTK 3.9, emoji |
| Labeling | Google Gemini API (google-generativeai 0.8) |
| Database | PostgreSQL (psycopg2) or MySQL (PyMySQL) via SQLAlchemy 2.0 + Alembic |
| Data | pandas, numpy, yfinance, scikit-learn |
| Ingestion | Telethon (Telegram), youtube-comment-downloader, Tweepy (Twitter/X) |
| Frontend | Next.js 14 (App Router), React 18, Tailwind CSS 3.4, Recharts 2.12, Lucide React |
| Logging | Loguru |
| Hosting | AWS EC2 (backend), Vercel (frontend) |

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL or MySQL connection string |
| `JWT_SECRET` | Yes | Secret key for signing JWT tokens (change from default!) |
| `JWT_EXPIRY_HOURS` | No | Token expiry in hours (default: 72) |
| `REDIS_URL` | No | Redis URL (only for Celery) |
| `TELEGRAM_API_ID` | For live | Telegram API ID |
| `TELEGRAM_API_HASH` | For live | Telegram API hash |
| `TELEGRAM_SESSION_NAME` | No | Telethon session name (default: `crowdpulse`) |
| `TWITTER_BEARER_TOKEN` | For live | Twitter/X API bearer token |
| `REDDIT_CLIENT_ID` | For live | Reddit OAuth app client ID ([create app](https://www.reddit.com/prefs/apps)) |
| `REDDIT_CLIENT_SECRET` | For live | Reddit OAuth app secret |
| `GEMINI_API_KEY` | For labeling | Google Gemini API key ([get free key](https://aistudio.google.com/apikey)) |
| `APP_ENV` | No | `development` or `production` |
| `LOG_LEVEL` | No | Logging level (default: `DEBUG`) |
| `CORS_ORIGINS` | No | Allowed origins (default: `http://localhost:3000`) |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL (default: `http://localhost:8000/api/v1`) |

## License

Educational and research use only. See PRODUCT_SPEC.md for full disclaimer.
