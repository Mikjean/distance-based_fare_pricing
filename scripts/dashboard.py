import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import numpy as np
from datetime import datetime
from collections import Counter
import re


st.set_page_config(page_title="Rwanda Distance-Based Fare Dashboard", layout="wide")

st.title("\U0001F4CA Rwanda Distance-Based Fare: Sentiment Dashboard")

# Load Data
df = pd.read_csv("data/sentiment_results_seeded.csv", parse_dates=["created_at"])
df["date"] = pd.to_datetime(df["created_at"].dt.date, errors="coerce")

# Sidebar Filters
st.sidebar.subheader("\U0001F50D Filter")
sentiments = st.sidebar.multiselect("Select Sentiment", options=df["label"].unique(), default=list(df["label"].unique()))
keywords = st.sidebar.text_input("Search Keyword")

filtered_df = df[df["label"].isin(sentiments)]
if keywords:
    filtered_df = filtered_df[filtered_df["cleaned"].str.contains(keywords.lower(), na=False)]

# Sentiment Trend
daily_sentiment = filtered_df.groupby(filtered_df["date"])["label"].value_counts().unstack().fillna(0)
st.subheader("\U0001F4C8 Sentiment Trend")
fig_trend = px.line(daily_sentiment, title="Sentiment Over Time", markers=True)
st.plotly_chart(fig_trend, use_container_width=True)

# Pie Chart: Sentiment Distribution
st.subheader("\U0001F4CA Sentiment Distribution")
sentiment_counts = filtered_df["label"].value_counts()
fig_pie = px.pie(values=sentiment_counts, names=sentiment_counts.index, title="Sentiment Share")
st.plotly_chart(fig_pie, use_container_width=True)

# Bar Chart: Top Keywords
def extract_keywords(text_series):
    words = " ".join(text_series).lower()
    words = re.findall(r'\b\w+\b', words)
    common_words = Counter(words).most_common(10)
    return pd.DataFrame(common_words, columns=["keyword", "count"])

st.subheader("\U0001F520 Top Keywords")
keyword_df = extract_keywords(filtered_df["cleaned"])
fig_keywords = px.bar(keyword_df, x="keyword", y="count", title="Top 10 Frequent Keywords")
st.plotly_chart(fig_keywords, use_container_width=True)

# Sentiment by Day of Week
st.subheader("Daily Sentiment Distribution")

daily_bar = daily_sentiment.reset_index().melt(id_vars="date", var_name="Sentiment", value_name="Count")
fig_bar = px.bar(
    daily_bar,
    x="date",
    y="Count",
    color="Sentiment",
    title="Daily Sentiment Breakdown",
    barmode="group",
    labels={"date": "Date", "Count": "Tweet Count"}
)
st.plotly_chart(fig_bar, use_container_width=True)

#combined sentiment analysis

def combined_sentiment_dashboard(daily_sentiment):
    # Convert date to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(daily_sentiment['date']):
        daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
    
    # 1. Detect spikes for each sentiment type
    spike_data = []
    for sentiment in ['positive', 'negative', 'neutral']:
        if sentiment in daily_sentiment.columns:
            threshold = daily_sentiment[sentiment].mean() + 2*daily_sentiment[sentiment].std()
            spikes = daily_sentiment[daily_sentiment[sentiment] > threshold].copy()
            spikes['sentiment_type'] = sentiment
            spikes['spike_value'] = spikes[sentiment]
            spike_data.append(spikes)
    
    all_spikes = pd.concat(spike_data) if spike_data else pd.DataFrame()
    
    # 2. Create combined interactive plot
    st.subheader("\U0001F5BC Combined Sentiment Analysis")
    
    fig = px.line(daily_sentiment, x='date', y=['positive', 'negative', 'neutral'],
                  labels={'value': 'Sentiment Score', 'variable': 'Sentiment Type'},
                  color_discrete_map={
                      'positive': 'green',
                      'negative': 'red',
                      'neutral': 'blue'
                  })
    
    # Add spike markers if any exist
    if not all_spikes.empty:
        fig.add_scatter(
            x=all_spikes['date'],
            y=all_spikes['spike_value'],
            mode='markers',
            marker=dict(color='black', size=10, symbol='diamond'),
            name='Spike Detected',
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Value: %{y:.2f}<extra></extra>"
        )
    
    fig.update_layout(
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. Summary statistics dashboard
    st.subheader(" Sentiment Summary")
    
    if not all_spikes.empty:
        # Create metrics columns
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Spikes", len(all_spikes))
        with cols[1]:
            st.metric("Positive Spikes", len(all_spikes[all_spikes['sentiment_type'] == 'positive']))
        with cols[2]:
            st.metric("Negative Spikes", len(all_spikes[all_spikes['sentiment_type'] == 'negative']))
        with cols[3]:
            st.metric("Neutral Spikes", len(all_spikes[all_spikes['sentiment_type'] == 'neutral']))
        
        # Show spike details in expandable section
        with st.expander("🔍 View Detailed Spike Analysis"):
            st.write(" Spike Statistics by Sentiment Type")
            spike_summary = all_spikes.groupby('sentiment_type').agg({
                'date': ['count', 'min', 'max'],
                'spike_value': ['mean', 'max']
            }).reset_index()
            
            # Flatten multi-index columns
            spike_summary.columns = [' '.join(col).strip() for col in spike_summary.columns.values]
            st.dataframe(spike_summary.style.format({
                'spike_value mean': '{:.2f}',
                'spike_value max': '{:.2f}',
                'date min': lambda x: x.strftime('%Y-%m-%d'),
                'date max': lambda x: x.strftime('%Y-%m-%d')
            }))
            
            st.write(" All Spike Events")
            st.dataframe(all_spikes[['date', 'sentiment_type', 'spike_value']]
                         .sort_values('date', ascending=False)
                         .reset_index(drop=True))
    else:
        st.success(" No significant sentiment spikes detected")
        st.write("All sentiment metrics within normal ranges")

# Sample data generation
dates = pd.date_range(end=datetime.today(), periods=30).tolist()
data = {
    "date": dates,
    "positive": np.concatenate([np.random.normal(50, 5, 25), [85, 30, 90, 35, 88]]),
    "negative": np.concatenate([np.random.normal(30, 3, 25), [15, 60, 10, 65, 12]]),
    "neutral": np.concatenate([np.random.normal(70, 7, 25), [120, 20, 125, 25, 122]])
}

daily_agg = pd.DataFrame(data)
combined_sentiment_dashboard(daily_agg)

# RECOMMENDATIONS SECTION
st.subheader(" Action Recommendations", divider="rainbow")

if 'label' in filtered_df.columns:
    sentiment_counts = filtered_df['label'].value_counts()
    
    # POSITIVE SENTIMENT RECOMMENDATIONS
    if sentiment_counts.get('positive', 0) > 0:
        with st.container(border=True):
            st.markdown("###  Positive Feedback")
            cols = st.columns([1,4])
            with cols[0]:
                st.metric("Count", sentiment_counts['positive'])
            with cols[1]:
                st.markdown("""
                - **Amplify** top-performing content
                - **Reward** engaged community members
                - **Document** successful patterns
                """)
    
    # NEGATIVE SENTIMENT RECOMMENDATIONS
    if sentiment_counts.get('negative', 0) > 0:
        with st.container(border=True):
            st.markdown("### Negative Feedback")
            cols = st.columns([1,4])
            with cols[0]:
                st.metric("Count", sentiment_counts['negative'])
            with cols[1]:
                st.markdown("""
                - **Prioritize** urgent complaints
                - **Analyze** root causes
                - **Follow-up** with affected users
                """)
    
    # NEUTRAL SENTIMENT RECOMMENDATIONS
    if sentiment_counts.get('neutral', 0) > 0:
        with st.container(border=True):
            st.markdown("### Neutral Feedback") 
            cols = st.columns([1,4])
            with cols[0]:
                st.metric("Count", sentiment_counts['neutral'])
            with cols[1]:
                st.markdown("""
                - **Improve** engagement hooks
                - **Survey** users for feedback
                - **Test** different messaging
                """)
    
    # GENERAL RECOMMENDATIONS
    st.success("### General Recommendation")
    st.markdown("""
    - Compare with historical trends
    - Set up automated alerts
    - Revisit weekly sentiment reports
    """)
else:
    st.warning("No sentiment data available")


# Word Cloud
st.subheader("\u2601\ufe0f Word Cloud")
st.image(Image.open("data/wordcloud.png"), use_column_width=True)

# Clickable Tweets Table
def make_clickable(text, tweet_id):
    url = f"https://twitter.com/i/web/status/{tweet_id}"
    return f'<a href="{url}" target="_blank">{text}</a>'

st.subheader("\U0001F4DD Tweets Summary by Sentiment")

if not filtered_df.empty:
    # Display counts by sentiment
    # st.write("### Tweet Count")
    sentiment_counts = filtered_df['label'].value_counts()
    
    for label, count in sentiment_counts.items():
        with st.expander(f"{label.capitalize()} Tweets: {count}", expanded=False):
            # Prepare the table
            tweet_table = filtered_df[filtered_df['label'] == label].copy()
            
            if "id" in tweet_table.columns:
                # Create clickable links if we have tweet IDs
                tweet_table["Tweet"] = tweet_table.apply(
                    lambda x: make_clickable(x["content"], x["id"]), 
                    axis=1
                )
                st.write(
                    tweet_table[["created_at", "Tweet", "label"]]
                    .sort_values("created_at", ascending=False)
                    .to_html(escape=False, index=False), 
                    unsafe_allow_html=True
                )
            else:
                # Fallback if no tweet IDs available
                st.dataframe(
                    tweet_table[["created_at", "content", "label"]]
                    .sort_values("created_at", ascending=False)
                    .reset_index(drop=True)
                )
else:
    st.info("No tweets found matching the selected filters")
