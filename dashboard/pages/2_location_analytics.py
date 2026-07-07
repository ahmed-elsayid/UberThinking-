"""
2_location_analytics.py
------------------------
Purpose:
    Dashboard page focused on geographic/zone-level ride patterns.

Responsibilities:
    - Display Top Pickup Zones and Top Dropoff Zones (bar charts / tables),
      using data/zone_lookup/ names for readability.
    - Display a map or heatmap of ride density by zone (if zone
      coordinates/boundaries are available; otherwise a ranked bar chart is
      an acceptable simplification).

Expected input:
    - Aggregated zone-level counts from output/parquet/aggregates/.
    - data/zone_lookup/taxi_zone_lookup.csv for zone names/boroughs.

Expected output:
    - Rendered Streamlit page with zone charts and/or map.

Dependencies:
    - streamlit, plotly.express
    - pandas
"""

# TODO: load zone aggregates -> render top-N bar charts and/or map.

"""
2_location_analytics.py
------------------------
Dashboard page focused on geographic/zone-level ride patterns: top
pickup/dropoff zones, using data/zone_lookup/ names for readability.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import plotly.express as px
import streamlit as st

from config.config import AGGREGATES_OUTPUT_PATH, ZONE_LOOKUP_PATH

st.set_page_config(page_title="Location Analytics | UberThinking", page_icon="🗺️", layout="wide")
st.title("🗺️ Location Analytics")


@st.cache_data(ttl=15)
def load_metric(metric_name: str) -> pd.DataFrame:
    path = os.path.join(AGGREGATES_OUTPUT_PATH, metric_name)
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_zone_lookup() -> pd.DataFrame:
    try:
        return pd.read_csv(ZONE_LOOKUP_PATH)
    except Exception:
        return pd.DataFrame()


top_pickup_df = load_metric("top_pickup_zones")
top_dropoff_df = load_metric("top_dropoff_zones")
zone_lookup_df = load_zone_lookup()

if top_pickup_df.empty and top_dropoff_df.empty:
    st.warning(
        "No zone aggregate data found yet. Start the producer and the "
        "streaming consumer, then come back to this page."
    )
else:
    left, right = st.columns(2)

    with left:
        st.subheader("Top Pickup Zones")
        if not top_pickup_df.empty:
            fig = px.bar(
                top_pickup_df.sort_values("trip_count"),
                x="trip_count",
                y="pickup_zone",
                orientation="h",
                title="Top Pickup Zones",
                labels={"pickup_zone": "Zone", "trip_count": "Trips"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top_pickup_df, use_container_width=True)
        else:
            st.info("No pickup zone data yet.")

    with right:
        st.subheader("Top Dropoff Zones")
        if not top_dropoff_df.empty:
            fig = px.bar(
                top_dropoff_df.sort_values("trip_count"),
                x="trip_count",
                y="dropoff_zone",
                orientation="h",
                title="Top Dropoff Zones",
                labels={"dropoff_zone": "Zone", "trip_count": "Trips"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top_dropoff_df, use_container_width=True)
        else:
            st.info("No dropoff zone data yet.")

    if not zone_lookup_df.empty and "Borough" in zone_lookup_df.columns:
        st.subheader("Zone Reference")
        st.caption(
            "Borough/Zone reference table from data/zone_lookup/, used to "
            "label the charts above."
        )
        st.dataframe(zone_lookup_df, use_container_width=True)
