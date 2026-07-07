"""
app.py
------
Purpose:
    Entry point for the Streamlit multipage dashboard. Streamlit
    automatically turns every file in dashboard/pages/ into a page in the
    sidebar navigation, so this file mainly sets shared/global config and
    a landing screen.

Responsibilities:
    - st.set_page_config(...) — title, icon, wide layout.
    - Display a short welcome/landing message describing the app and
      linking to each page (Overview, Location Analytics, Ride Explorer,
      Prediction, Streaming Monitor).
    - Initialize any shared resources needed across pages (e.g. a cached
      Spark session or cached data-loading functions), typically via
      @st.cache_resource / @st.cache_data helper functions defined here or
      in a shared utils module.

Expected input:
    - None directly; pages read from output/parquet/ and models/.

Expected output:
    - Rendered Streamlit landing page.

Dependencies:
    - streamlit
    - config/config.py

Run:
    streamlit run dashboard/app.py
"""


import os
import sys

# Streamlit only adds this script's own directory to sys.path, not the
# project root, so add the root explicitly for `config`/`ml` imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="UberThinking",
    page_icon="🚕",
    layout="wide",
)


@st.cache_data(ttl=30)
def load_parquet_dir(path: str) -> pd.DataFrame:
    """Cached helper: reads a Parquet directory into a pandas DataFrame.
    Shared across pages via `from dashboard.app import load_parquet_dir`.
    Returns an empty DataFrame if the path doesn't exist yet (e.g. before
    the streaming job has produced any output).
    """
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def main() -> None:
    st.title("🚕 UberThinking — Real-Time Ride Intelligence")
    st.markdown(
        """
        UberThinking simulates a live taxi-dispatch feed, processes it through
        Kafka and Spark Structured Streaming, and surfaces the results
        here. Use the sidebar to navigate:

        - **Overview** — high-level KPIs and charts for overall ride activity.
        - **Location Analytics** — busiest pickup/dropoff zones.
        - **Ride Explorer** — filter and browse individual cleaned rides.
        - **Prediction** — estimate a fare before a ride starts.
        - **Streaming Monitor** — near-real-time pipeline activity.
        """
    )
    st.info(
        "Data shown across these pages is produced by "
        "`streaming/spark_stream_consumer.py`. Start the producer and "
        "consumer first if pages appear empty."
    )


main()
