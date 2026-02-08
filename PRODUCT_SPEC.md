# CROWD-PULSE-FINAL.md

# CROWD PULSE

**Real-time Hinglish sentiment analysis and contrarian signals for the Indian equity market**

## 1. PROBLEM STATEMENT

In recent years, participation by retail investors in Indian equity markets has increased rapidly. Along with this growth, many new investors rely heavily on unregulated sources such as Telegram channels, YouTube videos, and social media posts for stock-related opinions. These platforms often promote short-term excitement rather than informed decision-making.

This behaviour has created three key challenges:

1. **Herd-driven trading behaviour**  
   Many retail investors follow social media tips without understanding risk, leading to sudden price surges and sharp losses, especially in small and mid-cap stocks.

2. **Poor understanding of Hinglish sentiment**  
   Most existing sentiment tools are designed for English and fail to capture Hinglish, Indian market slang, and emoji-based expressions commonly used by Indian investors.

3. **Lack of behavioural risk indicators**  
   There are limited tools that show when social media excitement is not supported by broader market participation, making it difficult to identify hype or panic phases.

## 2. PROPOSED SOLUTION

**Crowd Pulse** is an educational analytics platform designed to help users recognise crowd-driven behavioural risk in Indian equity markets. The system does **not** provide buy or sell recommendations. Instead, it offers interpretable indicators that highlight when retail investor sentiment becomes disconnected from broader market participation.

The platform focuses on three core insights:

1. **Hinglish-aware sentiment measurement**  
   Retail investor discussions in India frequently use Hinglish, market slang, and emojis that are poorly captured by conventional sentiment tools. Crowd Pulse measures collective sentiment in this linguistic context to reflect the true tone and intensity of retail opinion.

2. **Sentiment velocity as a herd signal**  
   Beyond sentiment levels, the platform tracks how rapidly sentiment changes over time. Sudden accelerations or reversals often signal emotionally driven or herd-like behaviour rather than gradual opinion formation.

3. **Sentiment-participation divergence (volume-based)**  
   Changes in social discussion **volume** (comment/post volume) are compared with delivery-based trading volume, used as a coarse proxy for relatively lower-turnover participation. Divergence between rising or falling discussion volume and stable market participation highlights potential hype or panic phases without attempting to predict price direction.

## 3. TECHNICAL ARCHITECTURE

The platform follows a **six-layer architecture processing pipeline**:

```
Layer 1: Data Extraction → Layer 2: Transformation → Layer 3: NLP Analysis → 
Layer 4: Divergence Engine → Layer 5: Storage → Layer 6: Visualisation
```

### Layer 1: Data Extraction and Collection
Publicly available social media comments and posts related to **Nifty 50** equities are collected alongside market data such as price, volume, and delivery-based trading metrics. Data sources and access methods are selected to support research and proof-of-concept development.

### Layer 2: Transformation
Raw textual data is processed through cleaning, normalisation, emoji handling, and tokenisation. This transformation layer prepares heterogeneous social media text for downstream linguistic analysis.

### Layer 3: NLP Analysis
A financial language model is adapted using a custom Hinglish-labelled dataset and lexicon augmentation. The model outputs sentiment scores at the comment and aggregate levels, along with rolling sentiment velocity metrics across multiple time windows.

### Layer 4: Divergence and Confidence Engine
Normalised discussion volume dynamics are statistically compared with delivery-based trading volume to compute divergence indicators. In parallel, a confidence score is generated based on model certainty, data availability, and short-term signal consistency.

### Layer 5: Storage
Processed sentiment metrics, divergence indicators, confidence scores, and associated metadata are stored in a time-series database. This layer enables historical analysis, backtesting, and efficient retrieval for visualisation.

### Layer 6: Visualisation
A web-based dashboard retrieves processed indicators from storage and presents **near real-time** and historical views of sentiment, behavioural risk, and confidence. For the MVP, update cadence is expected to be in the range of **15 minutes to 1 hour**, depending on free-tier rate limits and data availability. Visual elements prioritise interpretability and educational clarity.

## 4. METHODOLOGY

### 1. Dataset and Model Adaptation
A custom dataset of public comments is labelled as positive, negative, or neutral. For the MVP, labels are planned to be generated using AI-assisted labelling platforms to accelerate dataset creation. This dataset is used to adapt an existing financial language model to better capture Hinglish expressions, Indian market slang, and emoji-based sentiment.

### 2. Sentiment Velocity
Sentiment velocity is computed by calculating rolling sentiment averages over multiple time windows (e.g., 5-minute, 1-hour, 1-day) and measuring the rate of change. Velocity values are normalised to a 0-100 scale, with higher values indicating rapid shifts in collective opinion.

**Thresholds** are empirically tuned during exploratory backtesting and may vary depending on stock liquidity and data density.

### 3. Divergence and Confidence Scoring
The divergence indicator compares normalised changes in sentiment **discussion volume** with delivery-based trading volume to identify behavioural disconnects.

**Confidence Score** = `0.4 × Model Certainty + 0.3 × Data Sufficiency + 0.3 × Signal Consistency`

Where:
- **Model Certainty** reflects average sentiment classification probability
- **Data Sufficiency** reflects comment volume availability  
- **Signal Consistency** measures alignment across recent periods

## 5. TECHNICAL AND ECONOMICAL FEASIBILITY

| Component | Status | Cost | Notes |
|-----------|--------|------|-------|
| Telegram API (Telethon) | Available | Free (public data) | Access to public channels; subject to platform terms and rate limits |
| YouTube Comments (yt-dlp) | Available | Free (unofficial access) | Suitable for limited-scale data collection; throttling may occur |
| X / Twitter API | Limited | Free tier | Restricted endpoint access; used only for constrained MVP experimentation |
| NSE / BSE Market Data (yfinance) | Available (unofficial) | Free | Proxy data source suitable for research and proof-of-concept use |
| NLTK, SpaCy, regex | Available | Open-source | Widely used NLP libraries; no licensing restrictions |
| FinBERT-Base, LoRA, Pandas | Available | Free-tier cloud GPU | Suitable for prototyping and small-scale fine-tuning |
| Python, Z-score, Scikit-learn | Available | Free | Standard data science and statistical analysis libraries |
| PostgreSQL, Redis | Available | AWS free tier | Time-series storage and caching; self-hosting supported |
| AWS EC2 | Available | Free tier | Sufficient for MVP deployment and testing |
| React, Chart.js, Vercel | Available | Free tier | Suitable for hosting a lightweight, public-facing dashboard |

## 6. EXPECTED OUTCOMES

- ✅ Working Hinglish sentiment classifier achieving approximately **65-75% F1-score** on a custom-labelled dataset
- ✅ Sentiment velocity metrics identifying periods of rapid opinion shifts
- ✅ Divergence and confidence engine applied to **Nifty 50** for illustrative analysis
- ✅ Live, mobile-responsive dashboard demonstrating near real-time behavioural indicators (15 minutes to 1 hour update cadence)
- ✅ Proof-of-concept showcasing the feasibility of Hinglish financial NLP combined with crowd-risk analysis

## 7. REAL-WORLD APPLICATION

**Crowd Pulse** is intended as a **financial education and research tool**. It supports the study of behavioural finance in the Indian retail context and promotes more informed market participation by helping users recognise emotional and herd-driven risks.

The platform is suitable for:
- Academic demonstration
- Exploratory research
- Applied data science projects

## 8. DISCLAIMER
**This platform provides educational analytics only. It does NOT provide investment advice, buy/sell recommendations, or trading signals.**

## 9. REFERENCES

1. SEBI (2024). "Circular on Regulation of Investment Advisers and Finfluencers." *SEBI Circular No. SEBI/HO/MRD/DF/CIR/P/2024/125*.
2. Hinglish Sentiment Analysis Research (2023). "Sentiment Analysis in Hinglish Text." *IJRASET*, Vol. 11, Issue 9.
3. Jisem Journal (2024). "Expanding Research Horizons for Hinglish Text." *Journal of Indian Stock Exchange Market*.
4. Vipul Khatana (2017-Present). "Hinglish-Sentiment-Analysis." *GitHub Repository*.
5. Patel, R., & Sharma, A. (2024). "Machine Learning-Based Detection of Pump-and-Dump Schemes in Stock Markets." *arXiv:2412.18848*.
6. FinBERT: *https://huggingface.co/ProsusAI/finbert*
7. yfinance: *https://github.com/ranaroussi/yfinance*
