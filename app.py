import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from groq import Groq

# Page Config
st.set_page_config(
    page_title="Forex AI Signal & Calendar", page_icon="📈", layout="wide"
)

st.title("⚡ Forex Factory Live Calendar & AI Signal Predictor")
st.markdown(
    "Real-time economic calendar tracker powered by Groq AI for instant market predictions."
)

# Sidebar for API Key
st.sidebar.header("Configuration")
groq_api_key = st.sidebar.text_input(
    "Enter Groq API Key", type="password", help="Get your key from console.groq.com"
)

# Function to fetch Forex Factory Calendar (using public RSS/XML feed or scraper fallback)


@st.cache_data(ttl=300)  # Cache data for 5 minutes
def fetch_forex_calendar():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            return None
    except Exception as e:
        return None


# Load Data
with st.spinner("Fetching live Forex Factory data..."):
    df_calendar = fetch_forex_calendar()

if df_calendar is not None and not df_calendar.empty:
    # Rename/Clean columns for easy reading
    # Usually keys are: title, country, date, impact, forecast, previous, etc.
    st.sidebar.success("Live Calendar Connected Successfully!")

    # Filters
    st.sidebar.subheader("Filter News")
    impact_filter = st.sidebar.multiselect(
        "Select Impact Level",
        options=["High", "Medium", "Low", "None"],
        default=["High", "Medium"],
    )

    # Filter dataframe based on impact
    if "impact" in df_calendar.columns:
        filtered_df = df_calendar[
            df_calendar["impact"].isin(impact_filter)
        ].copy()
    else:
        filtered_df = df_calendar.copy()

    st.subheader(
        f"📅 Upcoming Economic Events ({len(filtered_df)} events found)"
    )

    # Display clean table
    st.dataframe(
        filtered_df[
            [
                col
                for col in [
                    "date",
                    "country",
                    "title",
                    "impact",
                    "forecast",
                    "previous",
                ]
                if col in filtered_df.columns
            ]
        ],
        use_container_width=True,
    )

    # AI Signal Prediction Section
    st.markdown("---")
    st.subheader("🤖 Groq AI Market Impact & Signal Analyzer")

    selected_event_title = st.selectbox(
        "Select an upcoming news event to analyze signal:",
        options=filtered_df["title"].unique()
        if "title" in filtered_df.columns
        else [],
    )

    if st.button("Generate AI Trade Signal") and selected_event_title:
        if not groq_api_key:
            st.error("Please enter your Groq API Key in the sidebar first.")
        else:
            # Extract specific event details
            event_row = filtered_df[
                filtered_df["title"] == selected_event_title
            ].iloc[0]

            prompt = f"""
            You are an expert forex trader and macroeconomic analyst. 
            Analyze the following upcoming economic event and predict the market signal and impact:
            
            Event Title: {event_row.get('title', 'N/A')}
            Country: {event_row.get('country', 'N/A')}
            Impact Level: {event_row.get('impact', 'N/A')}
            Forecast: {event_row.get('forecast', 'N/A')}
            Previous: {event_row.get('previous', 'N/A')}
            
            Provide:
            1. Short-term market direction (Bullish/Bearish/Neutral for relevant currency pairs).
            2. Expected volatility level.
            3. Detailed trading recommendation / risk warning.
            Keep it professional, concise, and structured.
            """

            try:
                client = Groq(api_key=groq_api_key)
                with st.spinner("Analyzing market patterns via Groq Llama 3..."):
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a senior forex technical and fundamental analyst.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.3,
                    )
                    ai_response = chat_completion.choices[0].message.content
                    st.success("Analysis Complete!")
                    st.markdown(ai_response)
            except Exception as e:
                st.error(f"Error connecting to Groq API: {e}")

else:
    st.warning(
        "Could not fetch data directly from standard feeds. Please check your internet connection or try again later."
    )
    st.info(
        "Tip: You can deploy this on Streamlit Community Cloud for free and access it anywhere!"
    )
