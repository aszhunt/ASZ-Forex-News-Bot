from datetime import datetime
import pandas as pd
import pytz
import requests
import streamlit as st

# ---------------- CONFIG ---------------- #
st.set_page_config(
    page_title="ASZ Pro News Bot", page_icon="🔴", layout="wide"
)

st.title("🔴 ASZ Forex News Bot (Advanced)")
st.caption("Live High Impact News + Smart Signal Engine")

# ---------------- FETCH NEWS ---------------- #


@st.cache_data(ttl=60)
def fetch_news():
  url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  try:
    res = requests.get(url, headers=headers, timeout=15)
    if res.status_code != 200:
      st.error(f"API Error: Status code {res.status_code}")
      return pd.DataFrame()

    data = res.json()
    if not isinstance(data, list):
      st.error("Invalid data format received from API.")
      return pd.DataFrame()

    pkt = pytz.timezone("Asia/Karachi")
    news_list = []

    for item in data:
      if item.get("impact", "").lower() != "high":
        continue

      # Convert time to PKT
      try:
        date_str = item.get("date", "")[:19]
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        dt = pytz.utc.localize(dt).astimezone(pkt)
        time_str = dt.strftime("%a %I:%M %p")
      except:
        time_str = "N/A"

      news_list.append({
          "Time (PKT)": time_str,
          "Currency": item.get("country", ""),
          "Event": item.get("title", ""),
          "Actual": item.get("actual", ""),
          "Forecast": item.get("forecast", ""),
          "Previous": item.get("previous", ""),
      })

    return pd.DataFrame(news_list)

  except Exception as e:
    st.error(f"Connection Error: {e}")
    return pd.DataFrame()


# ---------------- SIGNAL ENGINE ---------------- #
def get_signal(actual, forecast):
  try:
    a = float(str(actual).replace("K", "").replace("%", ""))
    f = float(str(forecast).replace("K", "").replace("%", ""))

    if a > f:
      return "BUY 🚀", "Actual > Forecast → Currency Strong"
    elif a < f:
      return "SELL 🔻", "Actual < Forecast → Currency Weak"
    else:
      return "WAIT ⏳", "No difference"
  except:
    return "WAIT ⏳", "Data not released"


# ---------------- UI ---------------- #
if st.button("🚀 Load News & Signals", type="primary"):
  with st.spinner("Fetching live market data..."):
    df = fetch_news()

  if df.empty:
    st.warning(
        "⚠️ No high-impact news found or Forex Factory API is currently"
        " blocking requests. Please try again in a few minutes."
    )
  else:
    st.success("✅ Live High Impact News Loaded Successfully")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Top News Signal")

    first = df.iloc[0]
    signal, reason = get_signal(first["Actual"], first["Forecast"])

    col1, col2 = st.columns(2)

    with col1:
      st.write(f"Currency: **{first['Currency']}**")
      st.write(f"Event: **{first['Event']}**")
      st.write(f"Time: **{first['Time (PKT)']}**")

    with col2:
      if "BUY" in signal:
        st.success(signal)
      elif "SELL" in signal:
        st.error(signal)
      else:
        st.warning(signal)

    st.info(f"🧠 Reason: {reason}")
else:
  st.info(
      "👈 Click the **'Load News & Signals'** button above to fetch the latest"
      " forex news."
  )

# ---------------- FOOTER ---------------- #
st.markdown("---")
st.caption("ASZ Advanced Bot | News-Based Smart Trading")
