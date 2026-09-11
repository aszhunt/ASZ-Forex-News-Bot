import pandas as pd
import requests
import streamlit as st
from groq import Groq

# Page Layout & Config
st.set_page_config(
    page_title="ASZ Forex News Bot", page_icon="⚡", layout="wide"
)

# Custom Neon Multi-Color CSS (Green, Blue, Purple Theme)
st.markdown(
    """
    <style>
    /* Main Background & Font Styling */
    .stApp {
        background: linear-gradient(135deg, #0d0f18 0%, #131722 50%, #1a0b2e 100%);
        color: #e0e6ed;
    }
    
    /* Neon Header Title Styling */
    .neon-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00ff87, #60efff, #b967ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        padding-top: 10px;
        text-shadow: 0 0 20px rgba(96, 239, 255, 0.3);
    }
    
    .neon-subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Custom Cards and Containers */
    div.stButton > button {
        background: linear-gradient(90deg, #00ff87, #60efff);
        color: #0b0e14;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 0 15px rgba(0, 255, 135, 0.4);
        transition: 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #60efff, #b967ff);
        color: #ffffff;
        box-shadow: 0 0 25px rgba(185, 103, 255, 0.6);
        transform: translateY(-2px);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f121a;
        border-right: 1px solid rgba(185, 103, 255, 0.2);
    }
    
    /* Dataframe Table styling customization */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(96, 239, 255, 0.3);
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(13, 15, 24, 0.8);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.markdown('<p class="neon-title">⚡ ASZ Forex News Bot ⚡</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="neon-subtitle">Advanced Real-Time Economic Calendar & AI Signal Intelligence Hub</p>',
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


# Main execution flow
with st.spinner("Connecting to global economic feeds..."):
    df = load_forex_data()

if not df.empty:
    st.sidebar.success("🟢 Live Feed Connected")

    # Normalize impact column
    if "impact" in df.columns:
        df["impact"] = df["impact"].fillna("None").astype(str)
        available_impacts = df["impact"].unique().tolist()
    else:
        available_impacts = ["High", "Medium", "Low", "None"]

    # Sidebar Filters
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

    # Filter dataframe
    if selected_impacts and "impact" in df.columns:
        filtered_df = df[df["impact"].isin(selected_impacts)].copy()
    else:
        filtered_df = df.copy()

    st.markdown(
        f"### 📅 Active Schedule Feed ({len(filtered_df)} events tracked)"
    )

    # Display clean table
    display_cols = [
        col
        for col in ["date", "country", "title", "impact", "forecast", "previous"]
        if col in filtered_df.columns
    ]
    st.dataframe(filtered_df[display_cols], use_container_width=True)

    # AI Prediction Section
    st.markdown("---")
    st.markdown("### 🤖 Groq AI Future Signal & Market Impact Intelligence")

    event_titles = (
        filtered_df["title"].unique().tolist()
        if "title" in filtered_df.columns
        else []
    )
    selected_event = st.selectbox(
        "Select target event for institutional signal analysis:",
        options=event_titles,
    )

    if st.button("🚀 Generate Predictive Signal") and selected_event:
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
            You are a master institutional forex desk trader and macro liquidity strategist.
            Analyze this upcoming economic release and synthesize a tactical trading blueprint:
            
            - Event Release: {event_row.get('title', 'N/A')}
            - Region/Currency: {event_row.get('country', 'N/A')}
            - Impact Level: {event_row.get('impact', 'N/A')}
            - Market Forecast: {event_row.get('forecast', 'N/A')}
            - Previous Data: {event_row.get('previous', 'N/A')}
            
            Structure your professional response with:
            1. Short-term Directional Bias (Bullish / Bearish / Range-bound for correlated pairs).
            2. Volatility Expectation (Low / Moderate / High-Impact Spike).
            3. Actionable Setup / Risk Assessment Protocol.
            """

            try:
                client = Groq(api_key=GROQ_API_KEY)
                with st.spinner(
                    "Running advanced AI macro computations via Groq..."
                ):
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
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
                    st.success("Signal Generated Successfully!")
                    st.markdown(ai_output)
            except Exception as ex:
                st.error(f"Groq API connection error: {ex}")
else:
    st.warning(
        "Unable to pull live calendar feed right now. Please refresh the page."
    )
