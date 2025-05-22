import pandas as pd
import random
from datetime import datetime, timedelta

# Load your existing data
df = pd.read_csv("data/sentiment_results.csv")

# Define sample fake tweet content
sample_texts = [
    "The new fare system is confusing",
    "I love the improvements in public transport!",
    "Not sure this is a good move by RURA",
    "Affordable fares help low-income earners",
    "What a mess at the Nyabugogo terminal!",
    "Transport in Rwanda is evolving fast",
    "They should listen to the passengers more",
    "Bus schedules need improvement"
]

# Define possible sentiments
sentiments = ["positive", "neutral", "negative"]

# Start from the last timestamp or today
start_time = datetime.now()
if 'created_at' in df.columns and not df.empty:
    start_time = pd.to_datetime(df['created_at'].iloc[-1]) + timedelta(minutes=1)

# Generate new fake rows
new_rows = []
for i in range(100):
    text = random.choice(sample_texts)
    sentiment = random.choice(sentiments)
    timestamp = start_time + timedelta(minutes=i)
    new_rows.append({
        "id": len(df) + i,
        "created_at": timestamp.isoformat(),
        "content": text,
        "sentiment": sentiment
    })

# Append and save
df_new = pd.DataFrame(new_rows)
df_combined = pd.concat([df, df_new], ignore_index=True)
df_combined.to_csv("data/sentiment_results.csv", index=False)

print("Seeded 100 new rows to 'sentiment_results_seeded.csv'")
