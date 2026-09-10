import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import ta

st.set_page_config(page_title="ASZ PRO NEWS BOT", layout="wide")

st.title("🔴 ASZ HYBRID NEWS + TECH BOT")

# ---------------- FETCH FOREX FACTORY ---------------- #
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

# ---------------- TECHNICAL ANALYSIS ---------------- #
def get_market_trend(pair="EURUSD=X"):
    df = yf.download(pair, period="1d", interval="5m")

    df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)

    last = df.iloc[-1]

    trend = "UP" if last["Close"] > last["EMA50"] else "DOWN"
    rsi = last["RSI"]

    return trend, rsi

# ---------------- NEWS LOGIC ---------------- #
def news_bias(event):
    event = event.lower()

    if "nfp" in event or "employment" in event:
        return "STRONG"
    elif "cpi" in event or "inflation" in event:
        return "VOLATILE"
    elif "rate" in event:
        return "VERY STRONG"
    else:
        return "NORMAL"

# ---------------- FINAL SIGNAL ---------------- #
def generate_signal(actual, forecast, trend, rsi):
    try:
        actual = float(actual.replace("K","").replace("%",""))
        forecast = float(forecast.replace("K","").replace("%",""))

        # News reaction
        if actual > forecast:
            news_dir = "BUY"
        elif actual < forecast:
            news_dir = "SELL"
        else:
            return "WAIT", "Neutral news"

        # Technical confirmation
        if news_dir == "BUY" and trend == "UP" and rsi > 50:
            return "STRONG BUY", "News + Trend + RSI aligned"
        elif news_dir == "SELL" and trend == "DOWN" and rsi < 50:
            return "STRONG SELL", "News + Trend + RSI aligned"
        else:
            return "WAIT", "Conflict between news & technical"

    except:
        return "WAIT", "Data not released yet"

# ---------------- UI ---------------- #
pair = st.selectbox("Select Pair", ["EURUSD=X","GBPUSD=X","USDJPY=X","XAUUSD=X"])

if st.button("🚀 Run PRO Analysis"):

    st.subheader("📊 Market Analysis")

    trend, rsi = get_market_trend(pair)

    st.write(f"Trend: **{trend}**")
    st.write(f"RSI: **{rsi:.2f}**")

    df = fetch_news()

    if df.empty:
        st.error("No news data found")
    else:
        st.subheader("🔴 High Impact News")
        st.dataframe(df)

        first = df.iloc[0]

        bias = news_bias(first["Event"])

        signal, reason = generate_signal(
            first["Actual"],
            first["Forecast"],
            trend,
            rsi
        )

        st.subheader("🔥 FINAL SIGNAL")

        if "BUY" in signal:
            st.success(signal)
        elif "SELL" in signal:
            st.error(signal)
        else:
            st.warning(signal)

        st.write(f"🧠 Reason: {reason}")
        st.write(f"📢 Event Strength: {bias}")
