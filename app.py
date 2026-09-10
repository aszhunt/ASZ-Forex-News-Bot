import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ASZ News Bot", layout="centered")

st.title("🔴 ASZ Forex News Bot (Simple & Working)")

# -------- FETCH NEWS (WORKING SOURCE) -------- #
@st.cache_data(ttl=300)
def fetch_news():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        news_list = []

        for item in data:
            if item.get("impact", "").lower() != "high":
                continue

            news_list.append({
                "Currency": item.get("country", ""),
                "Event": item.get("title", ""),
                "Actual": item.get("actual", ""),
                "Forecast": item.get("forecast", ""),
                "Previous": item.get("previous", ""),
                "Time": item.get("date", "")
            })

        return pd.DataFrame(news_list)

    except:
        return pd.DataFrame()

# -------- SIGNAL LOGIC -------- #
def get_signal(actual, forecast):
    try:
        a = float(str(actual).replace("K","").replace("%",""))
        f = float(str(forecast).replace("K","").replace("%",""))

        if a > f:
            return "BUY"
        elif a < f:
            return "SELL"
        else:
            return "WAIT"
    except:
        return "WAIT"

# -------- UI -------- #
if st.button("🚀 Fetch Forex News"):

    df = fetch_news()

    if df.empty:
        st.error("❌ News fetch nahi ho rahi (network ya source issue)")
    else:
        st.success("✅ Live High Impact News")
        st.dataframe(df)

        first = df.iloc[0]

        st.subheader("📊 Signal")

        signal = get_signal(first["Actual"], first["Forecast"])

        if signal == "BUY":
            st.success("BUY 🚀")
        elif signal == "SELL":
            st.error("SELL 🔻")
        else:
            st.warning("WAIT ⏳")

        st.write(f"Currency: {first['Currency']}")
        st.write(f"Event: {first['Event']}")
        st.write(f"Actual: {first['Actual']}")
        st.write(f"Forecast: {first['Forecast']}")
