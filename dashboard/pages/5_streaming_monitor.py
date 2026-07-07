"""
5_streaming_monitor.py
------------------------
Purpose:
    Dashboard page showing "live" streaming health/activity — closest
    thing to a real-time monitor within Streamlit's request/response model.

Responsibilities:
    - Periodically (e.g. via st.rerun on a timer, or a manual refresh
      button) reload the latest aggregate metrics.
    - Display: incoming ride count (recent window), current revenue
      (recent window), trips per minute, and the most recent ride record.

Expected input:
    - Latest rows from output/parquet/aggregates/ and output/parquet/rides/.

Expected output:
    - Rendered Streamlit page with near-real-time metrics.

Dependencies:
    - streamlit
    - pandas

Note:
    Streamlit is not a true streaming UI framework; document this
    limitation and the chosen refresh strategy (polling interval, manual
    refresh button, or st.autorefresh via a community component) in
    docs/architecture.md.
"""

# TODO: implement periodic/refresh-based loading of latest metrics.


"""
5_streaming_monitor.py
------------------------
Dashboard page showing "live" streaming health/activity — the closest
thing to a real-time monitor within Streamlit's request/response model.

Note on real-time limitations:
    Streamlit has no native push-based real-time updates; every page
    render is a fresh script run triggered by user interaction or a
    refresh. This page uses a manual "Refresh now" button plus an
    optional timed auto-refresh (via a short `time.sleep` + `st.rerun`
    loop, capped to avoid runaway reruns) as the polling strategy. This
    tradeoff is documented in docs/architecture.md.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import streamlit as st

from config.config import AGGREGATES_OUTPUT_PATH, RIDES_OUTPUT_PATH

st.set_page_config(page_title="Streaming Monitor | UberThinking", page_icon="📡", layout="wide")
st.title("📡 Streaming Monitor")

REFRESH_INTERVAL_SECONDS = 5


@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
def load_metric(metric_name: str) -> pd.DataFrame:
    path = os.path.join(AGGREGATES_OUTPUT_PATH, metric_name)
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
def load_latest_ride() -> pd.DataFrame:
    try:
        rides_df = pd.read_parquet(RIDES_OUTPUT_PATH)
        if rides_df.empty or "pickup_datetime" not in rides_df.columns:
            return rides_df
        return rides_df.sort_values("pickup_datetime", ascending=False).head(1)
    except Exception:
        return pd.DataFrame()


auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
st.sidebar.caption(f"Auto-refresh interval: {REFRESH_INTERVAL_SECONDS}s")
if st.sidebar.button("Refresh now"):
    st.cache_data.clear()
    st.rerun()

trips_window_df = load_metric("trips_per_window")
total_trips_df = load_metric("total_trips")
total_revenue_df = load_metric("total_revenue")
latest_ride_df = load_latest_ride()

if total_trips_df.empty:
    st.warning(
        "No streaming data found yet. Start the producer and the "
        "streaming consumer, then come back to this page."
    )
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trips Seen", f"{int(total_trips_df['total_trips'].iloc[0]):,}")
    col2.metric("Total Revenue", f"${total_revenue_df['total_revenue'].iloc[0]:,.2f}")

    if not trips_window_df.empty:
        latest_window = trips_window_df.sort_values("window", ascending=False).iloc[0]
        col3.metric("Trips (most recent 5-min window)", int(latest_window["trip_count"]))

    st.subheader("Trips per 5-Minute Window")
    if not trips_window_df.empty:
        st.line_chart(trips_window_df.set_index("window")["trip_count"])
    else:
        st.info("No windowed data yet.")

    st.subheader("Most Recent Ride")
    if not latest_ride_df.empty:
        st.dataframe(latest_ride_df, use_container_width=True)
    else:
        st.info("No ride records yet.")

if auto_refresh:
    time.sleep(REFRESH_INTERVAL_SECONDS)
    st.rerun()
