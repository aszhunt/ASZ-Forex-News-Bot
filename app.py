import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="ASZ Bot")

st.title("🔴 Forex News Bot")

def fetch_news():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        rows = []
        for item in data:
            if item.get("impact","").lower() != "high":
                continue

            rows.append({
                "Currency": item.get("country"),
                "Event": item.get("title"),
                "Actual": item.get("actual"),
                "Forecast": item.get("forecast")
            })

        return pd.DataFrame(rows)

    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

def signal(a, f):
    try:
        a = float(str(a).replace("K","").replace("%",""))
        f = float(str(f).replace("K","").replace("%",""))

        if a > f:
            return "BUY 🚀"
        elif a < f:
            return "SELL 🔻"
        else:
            return "WAIT ⏳"
    except:
        return "WAIT ⏳"

if st.button("Fetch News"):
    df = fetch_news()

    if df.empty:
        st.warning("No data")
    else:
        st.dataframe(df)

        first = df.iloc[0]
        st.subheader("Signal")

        st.write(signal(first["Actual"], first["Forecast"]))
