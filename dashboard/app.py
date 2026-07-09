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
from datetime import datetime

# Let this file import the modules that live in src/ and this dashboard/ dir.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import streamlit as st

import ui
from config import RIDES_OUTPUT_PATH

st.set_page_config(page_title="UberThinking — Dashboard", page_icon="🚕",
                   layout="wide", initial_sidebar_state="expanded")


@st.cache_data(ttl=5)
def load_rides() -> pd.DataFrame:
    """Reads all cleaned rides written by the streaming job (empty if none yet)."""
    try:
        return pd.read_parquet(RIDES_OUTPUT_PATH)
    except Exception:
        return pd.DataFrame()


ui.setup(active="dashboard")

rides = load_rides()
updated = datetime.now().strftime("%I:%M %p").lstrip("0")

# Header carries the Live badge, last-updated time, and the Refresh control.
if ui.header(
    "Dashboard",
    "Live NYC taxi analytics powered by Spark Structured Streaming.",
    icon_name="grid",
    live=not rides.empty,
    updated=updated,
    refresh=True,
):
    st.cache_data.clear()
    st.rerun()

if rides.empty:
    ui.status(is_live=False, count=0)
    ui.hint(
        "No rides yet — start the streaming job and generator, then hit Refresh.",
        icon_name="info",
    )
    ui.footer()
    st.stop()

# --- Overall KPIs ---
total_trips = len(rides)
total_revenue = rides["fare_amount"].sum()
average_fare = rides["fare_amount"].mean()
average_duration = rides["ride_duration_minutes"].mean()
average_distance = rides["trip_distance"].mean()

# Live incoming = how many new rides appeared since the last time this page ran.
previous_total = st.session_state.get("previous_total", total_trips)
live_incoming = max(total_trips - previous_total, 0)
st.session_state["previous_total"] = total_trips

ui.status(is_live=True, count=total_trips)

row1 = st.columns(3)
with row1[0]:
    ui.kpi_card("Total Trips", f"{total_trips:,}", "car")
with row1[1]:
    ui.kpi_card("Total Revenue", f"${total_revenue:,.0f}", "wallet")
with row1[2]:
    ui.kpi_card(
        "Live Incoming Rides",
        f"+{live_incoming:,}",
        "activity",
        sub="new since last refresh" if live_incoming else "hit Refresh to update",
        sub_positive=bool(live_incoming),
    )

row2 = st.columns(3)
with row2[0]:
    ui.kpi_card("Average Fare", f"${average_fare:,.2f}", "receipt")
with row2[1]:
    ui.kpi_card("Avg Trip Duration", f"{average_duration:.1f} min", "clock")
with row2[2]:
    ui.kpi_card("Avg Trip Distance", f"{average_distance:.2f} mi", "map-pin")

# --- Most recent rides, with friendly labels and formatting ---
recent = rides.sort_values("pickup_datetime", ascending=False).head(10).copy()
recent["fare_amount"] = recent["fare_amount"].map("${:,.2f}".format)
recent["trip_distance"] = recent["trip_distance"].map("{:.2f} mi".format)
recent["pickup_datetime"] = pd.to_datetime(recent["pickup_datetime"]).dt.strftime("%b %d, %H:%M")

display = recent[
    ["pickup_datetime", "pickup_zone", "dropoff_zone", "trip_distance", "fare_amount"]
].rename(
    columns={
        "pickup_datetime": "Pickup Time",
        "pickup_zone": "From",
        "dropoff_zone": "To",
        "trip_distance": "Distance",
        "fare_amount": "Fare",
    }
)
ui.panel(
    "Most Recent Rides",
    ui.table_html(display, numeric_cols=("Distance", "Fare")),
    icon_name="clock",
)

ui.footer()
