"""
1_Analytics.py  —  Page 2: Analytics
------------------------------------
Charts describing ride patterns: trips per hour, payment types, and the
busiest pickup zones. All computed with pandas from the rides Parquet.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

import pandas as pd
import plotly.express as px
import streamlit as st

from config import RIDES_OUTPUT_PATH

st.set_page_config(page_title="Analytics | UberThinking", page_icon="📊", layout="wide")


@st.cache_data(ttl=15)
def load_rides() -> pd.DataFrame:
    try:
        return pd.read_parquet(RIDES_OUTPUT_PATH)
    except Exception:
        return pd.DataFrame()


st.title("📊 Analytics")
rides = load_rides()

if rides.empty:
    st.warning("No rides yet. Start generate_stream.py and streaming_job.py, then refresh.")
    st.stop()

left, right = st.columns(2)

with left:
    st.subheader("Trips per Hour")
    by_hour = rides.groupby("pickup_hour").size().reset_index(name="trips")
    st.plotly_chart(
        px.bar(by_hour, x="pickup_hour", y="trips", labels={"pickup_hour": "Hour of day"}),
        use_container_width=True,
    )

with right:
    st.subheader("Payment Types")
    by_payment = rides.groupby("payment_type").size().reset_index(name="trips")
    st.plotly_chart(
        px.pie(by_payment, names="payment_type", values="trips"),
        use_container_width=True,
    )

st.subheader("Top 10 Pickup Zones")
top_zones = (
    rides.groupby("pickup_zone").size().reset_index(name="trips").sort_values("trips").tail(10)
)
st.plotly_chart(
    px.bar(top_zones, x="trips", y="pickup_zone", orientation="h"),
    use_container_width=True,
)
