"""
3_ride_explorer.py
-------------------
Purpose:
    Dashboard page letting users explore individual cleaned ride records
    with filters, for ad hoc investigation.

Responsibilities:
    - Provide filter widgets: date range, passenger count, payment type,
      pickup/dropoff zone.
    - Read cleaned ride-level data from output/parquet/rides/, apply the
      selected filters, and display the resulting rows in a table
      (st.dataframe).
    - Consider pagination/row limits for performance, since ride-level
      data can be large.

Expected input:
    - Parquet files under output/parquet/rides/.

Expected output:
    - Rendered Streamlit page with filter controls + a results table.

Dependencies:
    - streamlit
    - pandas
"""

# TODO: render filter widgets -> filter dataframe -> st.dataframe(...)

"""
3_ride_explorer.py
-------------------
Dashboard page letting users explore individual cleaned ride records with
filters, for ad hoc investigation. Reads output/parquet/rides/.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import streamlit as st

from config.config import RIDES_OUTPUT_PATH

st.set_page_config(page_title="Ride Explorer | UberThinking", page_icon="🔎", layout="wide")
st.title("🔎 Ride Explorer")

MAX_ROWS = 5000


@st.cache_data(ttl=15)
def load_rides() -> pd.DataFrame:
    try:
        return pd.read_parquet(RIDES_OUTPUT_PATH)
    except Exception:
        return pd.DataFrame()


rides_df = load_rides()

if rides_df.empty:
    st.warning(
        "No ride-level data found yet. Start the producer and the "
        "streaming consumer, then come back to this page."
    )
else:
    if "pickup_datetime" in rides_df.columns:
        rides_df["pickup_datetime"] = pd.to_datetime(rides_df["pickup_datetime"])

    st.sidebar.header("Filters")

    if "pickup_datetime" in rides_df.columns:
        min_date = rides_df["pickup_datetime"].min().date()
        max_date = rides_df["pickup_datetime"].max().date()
        date_range = st.sidebar.date_input(
            "Pickup date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
        )
    else:
        date_range = None

    passenger_options = sorted(rides_df["passenger_count"].dropna().unique().tolist()) if "passenger_count" in rides_df.columns else []
    selected_passengers = st.sidebar.multiselect("Passenger count", passenger_options, default=passenger_options)

    payment_options = sorted(rides_df["payment_type"].dropna().unique().tolist()) if "payment_type" in rides_df.columns else []
    selected_payments = st.sidebar.multiselect("Payment type", payment_options, default=payment_options)

    pickup_zone_options = sorted(rides_df["pickup_zone"].dropna().unique().tolist()) if "pickup_zone" in rides_df.columns else []
    selected_pickup_zones = st.sidebar.multiselect("Pickup zone", pickup_zone_options, default=pickup_zone_options)

    dropoff_zone_options = sorted(rides_df["dropoff_zone"].dropna().unique().tolist()) if "dropoff_zone" in rides_df.columns else []
    selected_dropoff_zones = st.sidebar.multiselect("Dropoff zone", dropoff_zone_options, default=dropoff_zone_options)

    filtered_df = rides_df.copy()

    if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["pickup_datetime"].dt.date >= start_date)
            & (filtered_df["pickup_datetime"].dt.date <= end_date)
        ]

    if selected_passengers:
        filtered_df = filtered_df[filtered_df["passenger_count"].isin(selected_passengers)]

    if selected_payments:
        filtered_df = filtered_df[filtered_df["payment_type"].isin(selected_payments)]

    if selected_pickup_zones:
        filtered_df = filtered_df[filtered_df["pickup_zone"].isin(selected_pickup_zones)]

    if selected_dropoff_zones:
        filtered_df = filtered_df[filtered_df["dropoff_zone"].isin(selected_dropoff_zones)]

    st.caption(f"Showing {min(len(filtered_df), MAX_ROWS):,} of {len(filtered_df):,} matching rides.")
    st.dataframe(filtered_df.head(MAX_ROWS), use_container_width=True)
