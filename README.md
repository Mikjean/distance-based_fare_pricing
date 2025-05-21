# Live Sentiment Analysis on Rwanda Distance-Based Fare System

## Features

- Collect tweets using Twitter API
- Store and analyze data with SQLite
- Sentiment analysis using VADER
- Keyword analysis and WordCloud
- Interactive Streamlit dashboard

## Setup Instructions

### 1. Clone project and setup environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
```

### 2. Set Twitter API Bearer Token

```bash
export TWITTER_BEARER_TOKEN='your_token_here'   # Linux/Mac
set TWITTER_BEARER_TOKEN=your_token_here        # Windows
```

### 3. Run data collection and analysis

```bash
python scripts/scrape_twitter.py
python scripts/analyze.py
```

### 4. Launch dashboard

```bash
streamlit run scripts/dashboard.py
```
