"""
2_Prediction.py  —  Page 3: Fare Prediction
-------------------------------------------
Enter trip details and get a predicted fare from the model trained by
train_model.py.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import streamlit as st

import ui
from config import ZONE_LOOKUP_PATH
from predict import predict_fare

st.set_page_config(page_title="Prediction | UberThinking", page_icon="💰",
                   layout="wide", initial_sidebar_state="expanded")


@st.cache_data(ttl=300)
def zone_names() -> list:
    try:
        return sorted(pd.read_csv(ZONE_LOOKUP_PATH)["Zone"].dropna().unique().tolist())
    except Exception:
        return []


def _default_index(zones: list, name: str, fallback: int) -> int:
    return zones.index(name) if name in zones else min(fallback, len(zones) - 1)


ui.setup(active="prediction")
ui.header(
    "Fare Prediction",
    "Estimate a NYC taxi fare using the trained Spark MLlib model.",
    icon_name="zap",
    badge="Random Forest",
)

zones = zone_names()

# Keep the form from stretching the full page width.
form_col, side_col = st.columns([3, 2])

with form_col:
    with st.form("prediction"):
        ui.section("Trip details", "route")
        col1, col2 = st.columns(2)
        with col1:
            distance = st.number_input("Trip distance (miles)", 0.1, 100.0, 3.0, 0.1,
                                       help="Straight-line trip length.")
            passengers = st.number_input("Passengers", 1, 6, 1)
            pickup_hour = st.slider("Pickup hour", 0, 23, 12,
                                    help="Hour of day the ride starts (0–23).")
        with col2:
            if zones:
                pickup_zone = st.selectbox(
                    "Pickup zone", zones,
                    index=_default_index(zones, "Midtown Center", 0))
                dropoff_zone = st.selectbox(
                    "Dropoff zone", zones,
                    index=_default_index(zones, "JFK Airport", 1))
            else:
                pickup_zone = st.text_input("Pickup zone")
                dropoff_zone = st.text_input("Dropoff zone")

        submitted = st.form_submit_button("Predict Fare", type="primary",
                                          use_container_width=True)

with side_col:
    if submitted:
        try:
            with st.spinner("Warming up Spark and scoring the trip… (first run takes a few seconds)"):
                fare = predict_fare(distance, passengers, pickup_hour, pickup_zone, dropoff_zone)

            per_mile = fare / distance if distance else 0.0
            ui.result_card(
                fare=f"${fare:,.2f}",
                route_from=pickup_zone,
                route_to=dropoff_zone,
                details=[
                    ("Distance", f"{distance:.1f} mi"),
                    ("Per mile", f"${per_mile:,.2f}"),
                    ("Passengers", str(passengers)),
                    ("Pickup hour", f"{pickup_hour:02d}:00"),
                    ("Model", "Random Forest"),
                ],
                note="Actual metered fares vary with traffic, tolls, and surcharges.",
            )
        except Exception as exc:
            st.error(f"Could not predict. Have you run `train_model.py` yet?\n\nDetails: {exc}")
    else:
        ui.hint("Enter trip details and click Predict Fare to estimate the cost.",
                icon_name="zap")

ui.footer()
