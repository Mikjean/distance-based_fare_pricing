import tweepy
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
QUERY = (
    '(fare OR pricing OR ticket OR transport OR bus OR payment) '
    '(Rwanda OR Kigali) ("distance-based" OR "per kilometer" OR "new system" OR "fare change") '
    '-is:retweet lang:en'
)

if not BEARER_TOKEN:
    raise EnvironmentError("❌ Twitter Bearer Token not found. Please set TWITTER_BEARER_TOKEN in your .env file.")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

def fetch_tweets(query, max_results=50):
    try:
        response = client.search_recent_tweets(
            query=query,
            tweet_fields=["created_at", "lang"],
            max_results=max_results
        )
    except tweepy.TweepyException as e:
        print(f"❌ Error fetching tweets: {e}")
        return []
    
    tweets = []
    if response.data:
        for tweet in response.data:
            tweets.append((tweet.id, tweet.created_at.isoformat(), tweet.text))
    return tweets

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Connect to the database
conn = sqlite3.connect("data/tweets.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS tweets (
    id INTEGER PRIMARY KEY,
    created_at TEXT,
    content TEXT
)
""")
conn.commit()

# Fetch and store tweets
tweets = fetch_tweets(QUERY)
print(f"✅ Fetched {len(tweets)} tweets.")

for tweet in tweets:
    try:
        c.execute("INSERT INTO tweets (id, created_at, content) VALUES (?, ?, ?)", tweet)
    except sqlite3.IntegrityError:
        continue  # Skip duplicates

conn.commit()
conn.close()
print("✅ Tweets saved to data/tweets.db")
