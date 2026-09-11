import pandas as pd
import requests
import streamlit as st
from groq import Groq

# Page Layout & Config
st.set_page_config(
    page_title="Forex AI Signal & Calendar", page_icon="📈", layout="wide"
)

st.title("⚡ Forex Factory Live Calendar & AI Signal Predictor")
st.markdown(
    "Real-time economic calendar tracker powered by Groq Llama 3 for instant market impact predictions."
)

# Sidebar Configuration
st.sidebar.header("🔑 Authentication")
groq_api_key = st.sidebar.text_input(
    "Enter Groq API Key", type="password", help="Get free key from console.groq.com"
)


# Fetch Data Function with fallback
@st.cache_data(ttl=300)
def load_forex_data():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# Main execution flow
with st.spinner("Fetching live market data..."):
    df = load_forex_data()

if not df.empty:
    st.sidebar.success("Live Market Connected!")

    # Normalize impact column strings safely
    if "impact" in df.columns:
        df["impact"] = df["impact"].fillna("None").astype(str)
        available_impacts = df["impact"].unique().tolist()
    else:
        available_impacts = ["High", "Medium", "Low", "None"]

    # Sidebar Filters
    st.sidebar.subheader("Filter Settings")
    selected_impacts = st.sidebar.multiselect(
        "Select Impact Levels",
        options=available_impacts,
        default=[
            imp for imp in ["High", "Medium"] if imp in available_impacts
        ]
        if available_impacts
        else [],
    )

    # Filter dataframe
    if selected_impacts and "impact" in df.columns:
        filtered_df = df[df["impact"].isin(selected_impacts)].copy()
    else:
        filtered_df = df.copy()

    st.subheader(
        f"📅 Economic Events Schedule ({len(filtered_df)} events listed)"
    )

    # Clean DataFrame display
    display_cols = [
        col
        for col in ["date", "country", "title", "impact", "forecast", "previous"]
        if col in filtered_df.columns
    ]
    st.dataframe(filtered_df[display_cols], use_container_width=True)

    # AI Prediction Section
    st.markdown("---")
    st.subheader("🤖 Groq AI Future Signal & Impact Generator")

    event_titles = (
        filtered_df["title"].unique().tolist()
        if "title" in filtered_df.columns
        else []
    )
    selected_event = st.selectbox(
        "Choose news event for deep analysis & signals:", options=event_titles
    )

    if st.button("Generate Signal") and selected_event:
        if not groq_api_key:
            st.error("Please provide your Groq API key in the sidebar.")
        else:
            event_row = filtered_df[
                filtered_df["title"] == selected_event
            ].iloc[0]

            prompt = f"""
            You are a veteran institutional forex trading desk manager and macro analyst.
            Analyze the following upcoming economic release and generate precise trading setups:
            
            - Event: {event_row.get('title', 'N/A')}
            - Country/Currency: {event_row.get('country', 'N/A')}
            - Impact: {event_row.get('impact', 'N/A')}
            - Forecast: {event_row.get('forecast', 'N/A')}
            - Previous: {event_row.get('previous', 'N/A')}
            
            Provide a structured breakdown containing:
            1. Short-term Market Direction (Bullish / Bearish / Neutral on major currency pairs).
            2. Expected Volatility Scale (Low / Medium / Extreme).
            3. Actionable Signal / Risk Warning for traders.
            Keep it clear, professional, and well-formatted.
            """

            try:
                client = Groq(api_key=groq_api_key)
                with st.spinner("Analyzing macro patterns with Groq..."):
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a professional financial market strategist.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.3,
                    )
                    ai_output = completion.choices[0].message.content
                    st.success("Analysis Generated Successfully!")
                    st.markdown(ai_output)
            except Exception as ex:
                st.error(f"Groq API connection error: {ex}")
else:
    st.warning(
        "Unable to pull live calendar feed right now. Please reload or check back shortly."
    )
