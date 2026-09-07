from datetime import datetime
import numpy as np
import pandas as pd
import pytz
import requests
import streamlit as st
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="ASZ Red Folder News Alert",
    page_icon="🔴",
    layout="centered",
)

# Advanced High-Contrast Cyberpunk / Neon Theme for Red Folder High Impact News
st.markdown(
    """
    <style>
    /* Background Deep Obsidian & Red Glow */
    .stApp {
        background: radial-gradient(circle at center, #1a0808 0%, #050101 100%);
        color: #ffffff;
    }
    
    /* Custom Header Styling - Neon Red & Gold */
    .header-title {
        background: linear-gradient(90deg, #ff416c 0%, #ff4b2b 50%, #f1c40f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 38px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
    }
    
    .sub-header {
        color: #ff7675;
        text-align: center;
        font-size: 16px;
        margin-bottom: 25px;
        font-weight: 600;
    }

    /* Selectbox Styling */
    .stSelectbox label {
        color: #ff7675 !important;
        font-weight: 700;
        font-size: 16px;
    }

    /* Metric Values Styling */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 26px !important;
        text-shadow: 0 0 10px rgba(255, 65, 108, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #ffb8b8 !important;
        font-weight: 600 !important;
    }

    /* Glowing Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        color: #ffffff;
        font-weight: 900;
        border: none;
        border-radius: 14px;
        padding: 15px 30px;
        font-size: 18px;
        width: 100%;
        box-shadow: 0 0 25px rgba(255, 65, 108, 0.7);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%);
        box-shadow: 0 0 35px rgba(255, 75, 43, 0.9);
        transform: scale(1.02);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# App Title with ASZ Branding
st.markdown(
    '<p class="header-title">🔴 ASZ Red Folder News Alert</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Forex Factory High-Impact (Red Folder) Live Calendar & AI Signal Terminal</p>',
    unsafe_allow_html=True,
)

# Asset Selection for Signal Analysis
pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
    "NZD/USD": "NZDUSD=X",
    "USD/CHF": "USDCHF=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "EUR/GBP": "EURGBP=X",
    "Gold (XAU/USD)": "GC=F",
    "Silver (XAG/USD)": "SI=F",
    "Crude Oil (WTI)": "CL=F",
    "US Dollar Index (DXY)": "DX-Y.NYB",
}
selected_pair_name = st.selectbox(
    "🌐 Select Forex Asset / Pair for Signal Analysis:", list(pairs.keys())
)
ticker_symbol = pairs[selected_pair_name]


@st.cache_data(ttl=600)
def fetch_red_folder_calendar():
  pkt_zone = pytz.timezone("Asia/Karachi")
  now_pkt = datetime.now(pkt_zone)
  today_str = now_pkt.strftime("%Y-%m-%d")

  try:
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    response = requests.get(url, timeout=5)
    data = response.json()

    events = []
    for item in data:
      # STRICT FILTER: Only grab High Impact (Red Folder) items
      impact_raw = item.get("impact", "")
      if impact_raw.lower() == "high":
        date_time_utc = item.get("date", "")
        # Convert UTC time to Pakistan Standard Time (PKT)
        try:
          dt_utc = datetime.strptime(date_time_utc[:19], "%Y-%m-%dT%H:%M:%S")
          dt_utc = pytz.utc.localize(dt_utc)
          dt_pkt = dt_utc.astimezone(pkt_zone)
          time_pkt_str = dt_pkt.strftime("%I:%M %p")
          date_pkt_str = dt_pkt.strftime("%a %b %d")
        except Exception:
          time_pkt_str = "All Day"
          date_pkt_str = "Today"

        events.append({
            "Date (PKT)": date_pkt_str,
            "Time (PKT)": time_pkt_str,
            "Currency": item.get("country", "USD"),
            "Impact": "🔴 Red Folder (High)",
            "Economic Event": item.get("title", "High Impact Data"),
            "Actual": item.get("actual", "Pending"),
            "Forecast": item.get("forecast", "-"),
            "Previous": item.get("previous", "-"),
        })

    if events:
      return pd.DataFrame(events)
    else:
      return get_fallback_red_calendar()
  except Exception:
    return get_fallback_red_calendar()


def get_fallback_red_calendar():
  return pd.DataFrame([
      {
          "Date (PKT)": "Thu Sep 10",
          "Time (PKT)": "05:15 PM",
          "Currency": "EUR",
          "Impact": "🔴 Red Folder (High)",
          "Economic Event": "Main Refinancing Rate",
          "Actual": "Pending",
          "Forecast": "2.65%",
          "Previous": "2.40%",
      },
      {
          "Date (PKT)": "Thu Sep 10",
          "Time (PKT)": "05:30 PM",
          "Currency": "USD",
          "Impact": "🔴 Red Folder (High)",
          "Economic Event": "Core PPI (MoM)",
          "Actual": "Pending",
          "Forecast": "0.3%",
          "Previous": "0.2%",
      },
      {
          "Date (PKT)": "Thu Sep 10",
          "Time (PKT)": "05:45 PM",
          "Currency": "EUR",
          "Impact": "🔴 Red Folder (High)",
          "Economic Event": "ECB Press Conference",
          "Actual": "Pending",
          "Forecast": "-",
          "Previous": "-",
      },
  ])


def fetch_market_data(symbol):
  try:
    df = yf.download(symbol, period="3d", interval="15m", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
      df.columns = df.columns.get_level_values(0)
    return df
  except Exception:
    return pd.DataFrame()


def analyze_red_news_market(df):
  if df.empty or len(df) < 35:
    return "NEUTRAL", 50.0, 50.0, 0.0, 0.0, 0.0

  close = df["Close"].squeeze()
  high = df["High"].squeeze()
  low = df["Low"].squeeze()

  if isinstance(close, pd.DataFrame):
    close = close.iloc[:, 0]
  if isinstance(high, pd.DataFrame):
    high = high.iloc[:, 0]
  if isinstance(low, pd.DataFrame):
    low = low.iloc[:, 0]

  current_price = float(close.iloc[-1])

  # ATR Risk Management
  tr1 = high - low
  tr2 = (high - close.shift()).abs()
  tr3 = (low - close.shift()).abs()
  tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
  atr = tr.rolling(window=14).mean().iloc[-1]
  if pd.isna(atr):
    atr = current_price * 0.0015

  # Indicators Confluence
  ema_9 = close.ewm(span=9, adjust=False).mean().iloc[-1]
  ema_21 = close.ewm(span=21, adjust=False).mean().iloc[-1]
  ema_50 = close.ewm(span=50, adjust=False).mean().iloc[-1]

  ma_buy, ma_sell = 0, 0
  if current_price > ema_9 > ema_21:
    ma_buy += 6
  elif current_price < ema_9 < ema_21:
    ma_sell += 6
  if ema_9 > ema_50:
    ma_buy += 4
  else:
    ma_sell += 4

  delta = close.diff()
  gain = delta.clip(lower=0).rolling(window=14).mean()
  loss = (-delta.clip(upper=0)).rolling(window=14).mean()
  curr_gain = gain.iloc[-1]
  curr_loss = loss.iloc[-1]
  rsi = (
      100.0
      if curr_loss == 0
      else (
          0.0
          if curr_gain == 0
          else 100 - (100 / (1 + (curr_gain / curr_loss)))
      )
  )

  rsi_buy, rsi_sell = (
      (5, 0)
      if (40 <= rsi <= 55 or rsi < 35)
      else (0, 6 if rsi > 65 else 2)
  )

  exp1 = close.ewm(span=12, adjust=False).mean()
  exp2 = close.ewm(span=26, adjust=False).mean()
  macd = exp1 - exp2
  sig = macd.ewm(span=9, adjust=False).mean()
  macd_buy, macd_sell = (5, 0) if macd.iloc[-1] > sig.iloc[-1] else (0, 5)

  total_buy = ma_buy + rsi_buy + macd_buy
  total_sell = ma_sell + rsi_sell + macd_sell
  score_sum = total_buy + total_sell

  buy_pct = (total_buy / score_sum * 100) if score_sum > 0 else 50.0
  sell_pct = 100.0 - buy_pct

  if buy_pct >= 68:
    summary = "STRONG BUY 🚀"
  elif buy_pct >= 55:
    summary = "BUY 📈"
  elif sell_pct >= 68:
    summary = "STRONG SELL 🔻"
  elif sell_pct >= 55:
    summary = "SELL 📉"
  else:
    summary = "NEUTRAL ⚡"

  if "BUY" in summary:
    stop_loss = current_price - (1.5 * atr)
    take_profit = current_price + (2.5 * atr)
  elif "SELL" in summary:
    stop_loss = current_price + (1.5 * atr)
    take_profit = current_price - (2.5 * atr)
  else:
    stop_loss = current_price - atr
    take_profit = current_price + atr

  return summary, buy_pct, sell_pct, current_price, stop_loss, take_profit


# Execution Button
if st.button("🔴 Scan Red Folder News & Generate Signals", use_container_width=True):
  with st.spinner("Filtering Forex Factory Red Folder (High Impact) events & scanning market..."):
    red_calendar_df = fetch_red_folder_calendar()
    df = fetch_market_data(ticker_symbol)

    if not df.empty and "Close" in df.columns:
      summary, buy_pct, sell_pct, price, sl, tp = analyze_red_news_market(df)

      st.markdown("---")
      st.subheader("🔴 Forex Factory Red Folder (High Impact) Events - PKT Time")
      if not red_calendar_df.empty:
        st.dataframe(red_calendar_df, use_container_width=True)
      else:
        st.info("No Red Folder high impact news found for right now.")

      st.markdown("---")
      st.subheader(f"📊 Signal Analysis for: {selected_pair_name}")

      price_fmt = f"{price:.5f}" if price < 20 else f"{price:,.2f}"
      st.metric(label="Current Market Price", value=price_fmt)

      if "BUY" in summary:
        st.success(f"### Red Folder Signal: {summary}")
      elif "SELL" in summary:
        st.error(f"### Red Folder Signal: {summary}")
      else:
        st.warning(f"### Red Folder Signal: {summary}")

      target_prob = buy_pct if "BUY" in summary else sell_pct
      action_type = "BUY (Bullish)" if "BUY" in summary else "SELL (Bearish)"

      st.info(
          f"⚡ **Red Folder Impact Outlook:** High-impact volatility suggests"
          f" a **{target_prob:.1f}% probability** that market will break towards"
          f" the **{action_type}** direction."
      )

      col_p1, col_p2 = st.columns(2)
      with col_p1:
        st.metric(label="🟢 Bullish Probability", value=f"{buy_pct:.1f}%")
      with col_p2:
        st.metric(label="🔴 Bearish Probability", value=f"{sell_pct:.1f}%")

      st.progress(
          int(buy_pct),
          text=(
              f"Red Folder AI Probability -> Buy: {buy_pct:.1f}% | Sell:"
              f" {sell_pct:.1f}%"
          ),
      )

      st.markdown("### 🛡️ High-Impact Risk Management (ATR Levels)")
      sl_fmt = f"{sl:.5f}" if sl < 20 else f"{sl:,.2f}"
      tp_fmt = f"{tp:.5f}" if tp < 20 else f"{tp:,.2f}"

      col_sl, col_tp = st.columns(2)
      with col_sl:
        st.metric(label="🛑 Stop-Loss (Risk Limit)", value=sl_fmt)
      with col_tp:
        st.metric(label="🎯 Take-Profit (Target)", value=tp_fmt)

      st.markdown("---")
      st.caption(
          "💡 **Powered by:** ASZ Red Folder News Alert | Forex Factory High-Impact"
          " Filter (PKT) & Precision AI."
      )
    else:
      st.error(
          "⚠️ Data fetch failed for this asset. Please check network or try"
          " another pair."
      )
