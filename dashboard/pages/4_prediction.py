"""
4_prediction.py
----------------
Purpose:
    Dashboard page where a user enters ride details and receives a
    predicted fare from the trained ML model.

Responsibilities:
    - Render input widgets: trip distance, passenger count, pickup hour,
      pickup zone, dropoff zone (dropdowns populated from
      data/zone_lookup/).
    - On submit, call ml/predict.py's predict_fare(...) with the given
      inputs.
    - Display the predicted fare clearly (e.g. st.metric or a highlighted
      st.success message).

Expected input:
    - User-entered values via Streamlit widgets.

Expected output:
    - Predicted fare amount displayed to the user.

Dependencies:
    - streamlit
    - ml/predict.py
"""


import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd
import streamlit as st

from config.config import ZONE_LOOKUP_PATH
from ml.predict import predict_fare

st.set_page_config(page_title="Prediction | UberThinking", page_icon="💰", layout="wide")
st.title("💰 Fare Prediction")


@st.cache_data(ttl=300)
def load_zone_options() -> list:
    try:
        zone_df = pd.read_csv(ZONE_LOOKUP_PATH)
        return sorted(zone_df["Zone"].dropna().unique().tolist())
    except Exception:
        return []


zone_options = load_zone_options()

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        distance = st.number_input("Trip distance (miles)", min_value=0.1, max_value=100.0, value=3.0, step=0.1)
        passengers = st.number_input("Passenger count", min_value=1, max_value=6, value=1, step=1)
        pickup_hour = st.slider("Pickup hour", min_value=0, max_value=23, value=12)

    with col2:
        if zone_options:
            pickup_zone = st.selectbox("Pickup zone", zone_options)
            dropoff_zone = st.selectbox("Dropoff zone", zone_options, index=min(1, len(zone_options) - 1))
        else:
            pickup_zone = st.text_input("Pickup zone")
            dropoff_zone = st.text_input("Dropoff zone")

    submitted = st.form_submit_button("Predict Fare")

if submitted:
    try:
        fare = predict_fare(
            distance=distance,
            passengers=passengers,
            pickup_hour=pickup_hour,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone,
        )
        st.success(f"Estimated fare: **${fare:,.2f}**")
    except Exception as exc:
        st.error(
            "Could not generate a prediction. Make sure the model has "
            f"been trained (see `ml/train_model.py`). Details: {exc}"
        )
