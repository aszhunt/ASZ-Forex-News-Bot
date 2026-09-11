import pandas as pd
import requests
import streamlit as st
from groq import Groq

# Page Layout & Config
st.set_page_config(
    page_title="ASZ Forex News Bot", page_icon="⚡", layout="wide"
)

# High-Readability Clean Neon & Dark Professional CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #38bdf8;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #0284c7, #2563eb);
        color: #ffffff;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.5rem;
        width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #0ea5e9, #3b82f6);
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.markdown('<p class="main-title">⚡ ASZ Forex News Bot ⚡</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Advanced Institutional Economic Calendar & High-Accuracy Directional Predictor</p>',
    unsafe_allow_html=True,
)

# Hardcoded Groq API Key
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"


# Fetch Data Function
@st.cache_data(ttl=300)
def load_forex_data():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


with st.spinner("Connecting to global liquidity feeds..."):
    df = load_forex_data()

if not df.empty:
    st.sidebar.success("🟢 Live Feed Active")

    if "impact" in df.columns:
        df["impact"] = df["impact"].fillna("None").astype(str)
        available_impacts = df["impact"].unique().tolist()
    else:
        available_impacts = ["High", "Medium", "Low", "None"]

    st.sidebar.markdown("### 🎛️ Filter Controls")
    selected_impacts = st.sidebar.multiselect(
        "Select Impact Severity",
        options=available_impacts,
        default=[
            imp for imp in ["High", "Medium"] if imp in available_impacts
        ]
        if available_impacts
        else [],
    )

    if selected_impacts and "impact" in df.columns:
        filtered_df = df[df["impact"].isin(selected_impacts)].copy()
    else:
        filtered_df = df.copy()

    st.markdown(
        f"### 📅 Live Schedule Stream ({len(filtered_df)} events tracked)"
    )

    display_cols = [
        col
        for col in ["date", "country", "title", "impact", "forecast", "previous"]
        if col in filtered_df.columns
    ]
    st.dataframe(filtered_df[display_cols], use_container_width=True)

    # Advanced Signal Prediction Section
    st.markdown("---")
    st.markdown(
        "### 🤖 High-Accuracy AI Signal Predictor (BUY / SELL Analysis)"
    )

    event_titles = (
        filtered_df["title"].unique().tolist()
        if "title" in filtered_df.columns
        else []
    )
    selected_event = st.selectbox(
        "Select target event for high-accuracy directional prediction:",
        options=event_titles,
    )

    if st.button("🎯 Execute High-Accuracy Direction Prediction") and selected_event:
        if (
            not GROQ_API_KEY
            or GROQ_API_KEY == "gsk_your_actual_groq_api_key_here"
        ):
            st.error(
                "Please replace 'gsk_your_actual_groq_api_key_here' in code with your real Groq API key."
            )
        else:
            event_row = filtered_df[
                filtered_df["title"] == selected_event
            ].iloc[0]

            prompt = f"""
            You are a senior institutional algorithmic forex trader and liquidity modeler with 20 years of experience.
            Analyze the following upcoming economic event data with high precision and predict the definitive market direction:
            
            - Event Title: {event_row.get('title', 'N/A')}
            - Country / Currency: {event_row.get('country', 'N/A')}
            - Impact Level: {event_row.get('impact', 'N/A')}
            - Market Consensus Forecast: {event_row.get('forecast', 'N/A')}
            - Previous Value: {event_row.get('previous', 'N/A')}
            
            Your response must strictly provide a high-accuracy trading blueprint structured as follows:
            1. **Primary Directional Signal:** CLEARLY state **BUY** or **SELL** (along with the specific major currency pair affected, e.g., EUR/USD, GBP/USD, USD/JPY).
            2. **Confidence Level:** Provide an estimated accuracy percentage score based on deviation potential.
            3. **Market Mechanics / Why:** Brief fundamental reasoning regarding how deviation between Forecast and Actual release triggers institutional order flow.
            4. **Execution Protocol:** Suggested entry stance, volatility caution, and invalidation risk level.
            """

            try:
                client = Groq(api_key=GROQ_API_KEY)
                with st.spinner(
                    "Running advanced macro predictive algorithms..."
                ):
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a professional elite algorithmic forex trading strategist.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                    )
                    ai_output = completion.choices[0].message.content
                    st.success("High-Accuracy Signal Computed Successfully!")
                    st.markdown(ai_output)
            except Exception as ex:
                st.error(f"Groq API connection error: {ex}")
else:
    st.warning(
        "Unable to pull live calendar feed right now. Please refresh the page."
    )
