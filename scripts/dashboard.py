import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

st.title("📊 Rwanda Distance-Based Fare: Sentiment Dashboard")

df = pd.read_csv("data/sentiment_results.csv", parse_dates=["created_at"])
df["date"] = df["created_at"].dt.date

st.sidebar.subheader("🔍 Filter")
sentiments = st.sidebar.multiselect("Select Sentiment", options=df["label"].unique(), default=list(df["label"].unique()))
keywords = st.sidebar.text_input("Search Keyword")

filtered_df = df[df["label"].isin(sentiments)]
if keywords:
    filtered_df = filtered_df[filtered_df["cleaned"].str.contains(keywords.lower(), na=False)]

daily_sentiment = filtered_df.groupby(filtered_df["date"])["label"].value_counts().unstack().fillna(0)

st.subheader("📈 Sentiment Trend")
fig = px.line(daily_sentiment, title="Sentiment Over Time", markers=True)
st.plotly_chart(fig)

st.subheader("☁️ Word Cloud")
st.image(Image.open("data/wordcloud.png"), use_column_width=True)

st.subheader("📝 Tweets")
st.dataframe(filtered_df[["created_at", "content", "label"]].sort_values("created_at", ascending=False))
