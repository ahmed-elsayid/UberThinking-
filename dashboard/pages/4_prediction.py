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

# TODO: render input widgets -> call predict_fare(...) -> display result.
