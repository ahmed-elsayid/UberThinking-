"""
1_Analytics.py  —  Page 2: Analytics
------------------------------------
Charts describing ride patterns: trips per hour, payment mix, busiest pickup
zones, and a borough breakdown. All computed with pandas from the rides
Parquet the streaming job writes.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import plotly.express as px
import streamlit as st

import ui
from config import RIDES_OUTPUT_PATH, ZONE_LOOKUP_PATH

st.set_page_config(page_title="Analytics | UberThinking", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")


@st.cache_data(ttl=15)
def load_rides() -> pd.DataFrame:
    try:
        return pd.read_parquet(RIDES_OUTPUT_PATH)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def zone_to_borough() -> dict:
    try:
        z = pd.read_csv(ZONE_LOOKUP_PATH)
        return dict(zip(z["Zone"], z["Borough"]))
    except Exception:
        return {}


ui.setup(active="analytics")

rides = load_rides()

ui.header("Analytics", "Ride patterns across time, payment, and geography.",
          icon_name="bar-chart", live=not rides.empty)

if rides.empty:
    ui.status(is_live=False, count=0)
    ui.hint("No rides yet — start the streaming job and generator, then refresh.")
    ui.footer()
    st.stop()

ui.status(is_live=True, count=len(rides))

# --- Context KPI strip ---
peak_hour = int(rides.groupby("pickup_hour").size().idxmax())
top_zone = rides["pickup_zone"].value_counts().idxmax()
k = st.columns(3)
with k[0]:
    ui.kpi_card("Peak Hour", f"{peak_hour:02d}:00", "clock", sub="busiest pickup hour")
with k[1]:
    ui.kpi_card("Busiest Pickup Zone", str(top_zone), "map-pin")
with k[2]:
    ui.kpi_card("Avg Tip", f"${rides['tip_amount'].mean():,.2f}", "receipt")

left, right = st.columns(2)

with left:
    with ui.card():
        ui.section("Trips per Hour", "clock")
        by_hour = rides.groupby("pickup_hour").size().reset_index(name="trips")
        fig = px.bar(by_hour, x="pickup_hour", y="trips",
                     labels={"pickup_hour": "Hour of day", "trips": "Trips"})
        fig.update_traces(marker_color=ui.AMBER_BRIGHT, marker_line_width=0,
                          hovertemplate="Hour %{x}:00<br>%{y:,} trips<extra></extra>")
        fig.update_yaxes(showgrid=True)
        ui.chart(fig, height=290, showlegend=False)

with right:
    with ui.card():
        ui.section("Payment Mix", "wallet")
        by_payment = (rides.groupby("payment_type").size()
                      .reset_index(name="trips").sort_values("trips", ascending=False))
        fig = px.pie(by_payment, names="payment_type", values="trips", hole=0.66)
        fig.update_traces(textposition="inside", textinfo="percent",
                          insidetextorientation="horizontal",
                          marker=dict(line=dict(color="white", width=2)),
                          hovertemplate="%{label}<br>%{value:,} trips (%{percent})<extra></extra>")
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.12,
                        xanchor="center", x=0.5),
            annotations=[dict(text=f"{len(rides):,}<br>rides", x=0.5, y=0.5,
                              font=dict(size=15, color=ui.NAVY), showarrow=False)],
        )
        ui.chart(fig, height=290)

with ui.card():
    ui.section("Top 10 Pickup Zones", "map-pin")
    top_zones = (
        rides.groupby("pickup_zone").size().reset_index(name="trips")
        .sort_values("trips").tail(10)
    )
    fig = px.bar(top_zones, x="trips", y="pickup_zone", orientation="h",
                 labels={"trips": "Trips", "pickup_zone": ""})
    fig.update_traces(marker_color="#9AA6BC", marker_line_width=0,
                      hovertemplate="%{y}<br>%{x:,} trips<extra></extra>")
    fig.update_xaxes(showgrid=True)
    ui.chart(fig, height=360, showlegend=False)

# --- Borough breakdown (uses the borough column from the zone lookup) ---
mapping = zone_to_borough()
if mapping:
    with ui.card():
        ui.section("Trips by Borough", "bar-chart")
        rides = rides.assign(borough=rides["pickup_zone"].map(mapping).fillna("Unknown"))
        by_boro = (rides.groupby("borough").size().reset_index(name="trips")
                   .sort_values("trips", ascending=False))
        fig = px.bar(by_boro, x="borough", y="trips",
                     labels={"borough": "", "trips": "Trips"},
                     color="borough", color_discrete_sequence=ui.CHART_COLORS)
        fig.update_traces(marker_line_width=0,
                          hovertemplate="%{x}<br>%{y:,} trips<extra></extra>")
        ui.chart(fig, height=340, showlegend=False)

ui.footer()
