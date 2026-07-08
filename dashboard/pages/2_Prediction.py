"""
2_Prediction.py  —  Page 3: Fare Prediction
-------------------------------------------
Enter trip details and get a predicted fare from the model trained by
train_model.py.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

import pandas as pd
import streamlit as st

from config import ZONE_LOOKUP_PATH
from predict import predict_fare

st.set_page_config(page_title="Prediction | UberThinking", page_icon="💰", layout="wide")


@st.cache_data(ttl=300)
def zone_names() -> list:
    try:
        return sorted(pd.read_csv(ZONE_LOOKUP_PATH)["Zone"].dropna().unique().tolist())
    except Exception:
        return []


st.title("💰 Fare Prediction")
zones = zone_names()

with st.form("prediction"):
    col1, col2 = st.columns(2)
    with col1:
        distance = st.number_input("Trip distance (miles)", 0.1, 100.0, 3.0, 0.1)
        passengers = st.number_input("Passengers", 1, 6, 1)
        pickup_hour = st.slider("Pickup hour", 0, 23, 12)
    with col2:
        if zones:
            pickup_zone = st.selectbox("Pickup zone", zones)
            dropoff_zone = st.selectbox("Dropoff zone", zones, index=min(1, len(zones) - 1))
        else:
            pickup_zone = st.text_input("Pickup zone")
            dropoff_zone = st.text_input("Dropoff zone")

    submitted = st.form_submit_button("Predict Fare")

if submitted:
    try:
        fare = predict_fare(distance, passengers, pickup_hour, pickup_zone, dropoff_zone)
        st.success(f"Estimated fare: **${fare:,.2f}**")
    except Exception as exc:
        st.error(f"Could not predict. Have you run train_model.py yet? Details: {exc}")
