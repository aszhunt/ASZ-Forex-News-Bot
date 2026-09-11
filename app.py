import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Forex News AI Signal", layout="wide")

st.title("📊 Forex News + AI Signal (REAL DATA)")

# ----------------------------
# FETCH REAL DATA (API)
# ----------------------------
@st.cache_data(ttl=300)
def get_news():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

    try:
        data = requests.get(url, timeout=10).json()

        rows = []

        for item in data:
            try:
                dt = item.get("date", "")
                currency = item.get("country", "")
                impact = item.get("impact", "")
                event = item.get("title", "")

                # Convert datetime
                if dt:
                    dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                    date = dt_obj.strftime("%Y-%m-%d")
                    time = dt_obj.strftime("%H:%M")
                else:
                    date = "N/A"
                    time = "N/A"

                rows.append({
                    "Date": date,
                    "Time": time,
                    "Currency": currency,
                    "Impact": impact,
                    "Event": event
                })

            except:
                continue

        df = pd.DataFrame(rows)

        if df.empty:
            return pd.DataFrame(columns=["Date","Time","Currency","Impact","Event"])

        return df

    except:
        return pd.DataFrame(columns=["Date","Time","Currency","Impact","Event"])


df = get_news()

# ----------------------------
# SAFETY CHECK
# ----------------------------
for col in ["Date","Time","Currency","Impact","Event"]:
    if col not in df.columns:
        df[col] = "N/A"

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("Filters")

currency_filter = st.sidebar.multiselect(
    "Currency",
    df["Currency"].unique(),
    default=df["Currency"].unique()
)

impact_filter = st.sidebar.multiselect(
    "Impact",
    df["Impact"].unique(),
    default=df["Impact"].unique()
)

filtered_df = df[
    (df["Currency"].isin(currency_filter)) &
    (df["Impact"].isin(impact_filter))
]

# ----------------------------
# AI SIGNAL LOGIC (BETTER)
# ----------------------------
def generate_signal(impact):
    impact = impact.lower()

    if "high" in impact:
        return "🔥 STRONG MOVE EXPECTED"
    elif "medium" in impact:
        return "⚠️ MEDIUM VOLATILITY"
    else:
        return "⏳ WAIT / LOW IMPACT"

filtered_df["Signal"] = filtered_df["Impact"].apply(generate_signal)

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("📅 Live Forex News (Date + Time FIXED)")
st.dataframe(filtered_df, use_container_width=True)

# ----------------------------
# SUMMARY
# ----------------------------
st.subheader("🧠 Market Insight")

if filtered_df["Impact"].str.contains("High", case=False).any():
    st.success("⚡ High Impact News Coming → Big Moves Possible")
else:
    st.info("Market Calm")

# ----------------------------
# SIGNAL BOARD
# ----------------------------
st.subheader("📈 Signals")

for _, row in filtered_df.iterrows():
    st.write(f"{row['Date']} {row['Time']} | {row['Currency']} | {row['Event']} → {row['Signal']}")
