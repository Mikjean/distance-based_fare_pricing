import sqlite3
import pandas as pd
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

nltk.download("vader_lexicon")

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

conn = sqlite3.connect("data/tweets.db")
df = pd.read_sql_query("SELECT * FROM tweets", conn)
conn.close()

df["cleaned"] = df["content"].apply(clean_text)

sid = SentimentIntensityAnalyzer()
df["sentiment_score"] = df["cleaned"].apply(lambda x: sid.polarity_scores(x)["compound"])
df["label"] = df["sentiment_score"].apply(lambda score: "positive" if score > 0.05 else "negative" if score < -0.05 else "neutral")
df["created_at"] = pd.to_datetime(df["created_at"])
df.to_csv("data/sentiment_results.csv", index=False)

text = " ".join(df["cleaned"])
wordcloud = WordCloud(width=800, height=400).generate(text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.tight_layout()
plt.savefig("data/wordcloud.png")
plt.close()
