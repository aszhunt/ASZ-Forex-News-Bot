import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import random

st.set_page_config(page_title="Forex News AI Signal", layout="wide")

st.title("📊 Forex Factory News + AI Signal App")

# ----------------------------
# FETCH FOREX FACTORY DATA
# ----------------------------
@st.cache_data
def get_forex_news():
    url = "https://www.forexfactory.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    events = soup.find_all("tr", class_="calendar__row")

    data = []

    for event in events:
        try:
            currency = event.find("td", class_="calendar__currency").text.strip()
            impact = event.find("td", class_="impact").find("span")["title"]
            title = event.find("td", class_="calendar__event").text.strip()
            time = event.find("td", class_="calendar__time").text.strip()

            data.append({
                "Currency": currency,
                "Impact": impact,
                "Event": title,
                "Time": time
            })
        except:
            pass

    return pd.DataFrame(data)

df = get_forex_news()

# ----------------------------
# FILTERS
# ----------------------------
st.sidebar.header("Filters")

currency_filter = st.sidebar.multiselect(
    "Select Currency",
    options=df["Currency"].unique(),
    default=df["Currency"].unique()
)

impact_filter = st.sidebar.multiselect(
    "Impact Level",
    options=df["Impact"].unique(),
    default=df["Impact"].unique()
)

filtered_df = df[
    (df["Currency"].isin(currency_filter)) &
    (df["Impact"].isin(impact_filter))
]

# ----------------------------
# FAKE AI SIGNAL GENERATOR
# ----------------------------
def generate_signal(impact):
    if "High" in impact:
        return random.choice(["🔥 STRONG BUY", "🔥 STRONG SELL"])
    elif "Medium" in impact:
        return random.choice(["BUY", "SELL"])
    else:
        return "WAIT"

filtered_df["Signal"] = filtered_df["Impact"].apply(generate_signal)

# ----------------------------
# UI DISPLAY
# ----------------------------
st.subheader("📅 Live News Calendar")

st.dataframe(filtered_df, use_container_width=True)

# ----------------------------
# AUTO ANALYSIS SUMMARY
# ----------------------------
st.subheader("🧠 AI Summary")

high_impact = filtered_df[filtered_df["Impact"].str.contains("High")]

if not high_impact.empty:
    st.success("⚡ High Impact News Detected → Market may be volatile")
else:
    st.info("No major volatility expected")

# ----------------------------
# SIGNAL BOARD
# ----------------------------
st.subheader("📈 Quick Signals")

for i, row in filtered_df.iterrows():
    st.write(f"{row['Currency']} | {row['Event']} → {row['Signal']}")
