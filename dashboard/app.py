"""
app.py  —  Page 1: Dashboard
----------------------------
Shows the overall KPIs and a live incoming-ride counter. Reads the rides
Parquet folder that the streaming job keeps appending to.

Run:
    streamlit run dashboard/app.py
"""

import os
import sys

# Let this file import the modules that live in src/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pandas as pd
import streamlit as st

from config import RIDES_OUTPUT_PATH

st.set_page_config(page_title="UberThinking", page_icon="🚕", layout="wide")


@st.cache_data(ttl=5)
def load_rides() -> pd.DataFrame:
    """Reads all cleaned rides written by the streaming job (empty if none yet)."""
    try:
        return pd.read_parquet(RIDES_OUTPUT_PATH)
    except Exception:
        return pd.DataFrame()


st.title("🚕 UberThinking — Dashboard")
st.caption("Live taxi analytics powered by Spark Structured Streaming.")

if st.button("🔄 Refresh"):
    st.cache_data.clear()

rides = load_rides()

if rides.empty:
    st.warning("No rides yet. Start generate_stream.py and streaming_job.py, then refresh.")
    st.stop()

# --- Overall KPIs ---
total_trips = len(rides)
total_revenue = rides["fare_amount"].sum()
average_fare = rides["fare_amount"].mean()
average_duration = rides["ride_duration_minutes"].mean()

# Live incoming = how many new rides appeared since the last time this page ran.
previous_total = st.session_state.get("previous_total", total_trips)
live_incoming = max(total_trips - previous_total, 0)
st.session_state["previous_total"] = total_trips

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Trips", f"{total_trips:,}")
c2.metric("Total Revenue", f"${total_revenue:,.0f}")
c3.metric("Average Fare", f"${average_fare:,.2f}")
c4.metric("Avg Trip Duration", f"{average_duration:.1f} min")
c5.metric("Live Incoming Rides", f"+{live_incoming}")

st.divider()
st.subheader("Most Recent Rides")
recent = rides.sort_values("pickup_datetime", ascending=False).head(10)
st.dataframe(
    recent[["pickup_datetime", "pickup_zone", "dropoff_zone", "trip_distance", "fare_amount"]],
    use_container_width=True,
)
