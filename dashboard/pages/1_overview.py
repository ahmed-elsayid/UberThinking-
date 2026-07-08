"""
1_overview.py
-------------
Dashboard page showing high-level KPIs (total trips, revenue, average fare
and duration) plus peak-hour and payment-type charts, read from the
aggregate Parquet snapshots under output/parquet/aggregates/.
"""


import os
import sys

# Streamlit only adds this script's own directory to sys.path, not the
# project root, so add the root explicitly for `config`/`ml` imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import plotly.express as px
import streamlit as st

from config.config import AGGREGATES_OUTPUT_PATH

st.set_page_config(page_title="Overview | UberThinking", page_icon="🚕", layout="wide")
st.title("📊 Overview")


@st.cache_data(ttl=15)
def load_metric(metric_name: str) -> pd.DataFrame:
    path = os.path.join(AGGREGATES_OUTPUT_PATH, metric_name)
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


total_trips_df = load_metric("total_trips")
total_revenue_df = load_metric("total_revenue")
average_fare_df = load_metric("average_fare")
average_duration_df = load_metric("average_duration")
trips_by_hour_df = load_metric("trips_by_hour")
payment_distribution_df = load_metric("payment_distribution")

if total_trips_df.empty:
    st.warning(
        "No aggregate data found yet. Start the producer and the "
        "streaming consumer, then come back to this page."
    )
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trips", f"{int(total_trips_df['total_trips'].iloc[0]):,}")
    col2.metric("Total Revenue", f"${total_revenue_df['total_revenue'].iloc[0]:,.2f}")
    col3.metric("Average Fare", f"${average_fare_df['average_fare'].iloc[0]:,.2f}")
    col4.metric(
        "Average Duration",
        f"{average_duration_df['average_duration_minutes'].iloc[0]:.1f} min",
    )

    st.subheader("Peak Hours")
    left, right = st.columns(2)

    with left:
        if not trips_by_hour_df.empty:
            fig = px.bar(
                trips_by_hour_df,
                x="pickup_hour",
                y="trip_count",
                title="Trips per Hour (Peak-Hour Analysis)",
                labels={"pickup_hour": "Hour of Day", "trip_count": "Trips"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly data yet.")

    with right:
        if not payment_distribution_df.empty:
            fig = px.pie(
                payment_distribution_df,
                names="payment_type",
                values="trip_count",
                title="Payment Type Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No payment data yet.")
