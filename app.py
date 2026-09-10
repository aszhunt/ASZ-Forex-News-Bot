import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from groq import Groq

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="ASZ SIMPLE PRO BOT", layout="centered")
st.title("🔴 ASZ News + AI Signal Bot")

# 👉 Apni Groq API key yahan lagao
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ---------------- FETCH NEWS ---------------- #
@st.cache_data(ttl=300)
def fetch_news():
    url = "https://www.forexfactory.com/calendar"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("tr.calendar__row")

    data = []

    for row in rows:
        try:
            impact = row.select_one(".impact").text.strip()
            if "High" not in impact:
                continue

            currency = row.select_one(".calendar__currency").text.strip()
            event = row.select_one(".calendar__event").text.strip()
            actual = row.select_one(".calendar__actual").text.strip()
            forecast = row.select_one(".calendar__forecast").text.strip()
            previous = row.select_one(".calendar__previous").text.strip()

            data.append({
                "Currency": currency,
                "Event": event,
                "Actual": actual,
                "Forecast": forecast,
                "Previous": previous
            })
        except:
            continue

    return pd.DataFrame(data)

# ---------------- BASIC SIGNAL ---------------- #
def basic_signal(actual, forecast):
    try:
        a = float(actual.replace("K","").replace("%",""))
        f = float(forecast.replace("K","").replace("%",""))

        if a > f:
            return "BUY"
        elif a < f:
            return "SELL"
        else:
            return "WAIT"
    except:
        return "WAIT"

# ---------------- GROQ AI ANALYSIS ---------------- #
def ai_analysis(event, currency, actual, forecast, previous):
    prompt = f"""
You are a professional forex analyst.

Event: {event}
Currency: {currency}
Actual: {actual}
Forecast: {forecast}
Previous: {previous}

Give:
1. BUY or SELL or WAIT
2. Short reason
3. Market expectation

Be precise and realistic.
"""

    try:
        chat = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}]
        )
        return chat.choices[0].message.content
    except:
        return "AI not available"

# ---------------- UI ---------------- #
if st.button("🚀 Fetch News & Generate Signal"):

    df = fetch_news()

    if df.empty:
        st.error("No news data found (Forex Factory may block request)")
    else:
        st.subheader("🔴 High Impact News")
        st.dataframe(df)

        first = df.iloc[0]

        st.subheader("📊 BASIC SIGNAL")

        signal = basic_signal(first["Actual"], first["Forecast"])

        if signal == "BUY":
            st.success("BUY 🚀")
        elif signal == "SELL":
            st.error("SELL 🔻")
        else:
            st.warning("WAIT ⏳")

        st.subheader("🧠 AI ANALYSIS (Groq)")

        ai_result = ai_analysis(
            first["Event"],
            first["Currency"],
            first["Actual"],
            first["Forecast"],
            first["Previous"]
        )

        st.write(ai_result)

# ---------------- FOOTER ---------------- #
st.caption("ASZ Simple Pro Bot | News + AI Hybrid")
