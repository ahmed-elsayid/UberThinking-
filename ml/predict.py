"""
predict.py
----------
Purpose:
    Loads the trained fare-prediction PipelineModel and exposes a simple
    function the Streamlit dashboard can call to predict a fare from
    user-provided inputs.

Responsibilities:
    - Load the saved PipelineModel from MODEL_PATH once (cache it — avoid
      reloading on every prediction request).
    - Accept user inputs matching the training features:
        - trip_distance, passenger_count, pickup_hour,
          pickup_zone, dropoff_zone
    - Wrap inputs into a single-row Spark DataFrame with the same schema
      used during training.
    - Call model.transform(...) and extract the predicted fare_amount.
    - Return a plain Python float (not a Spark type) to the caller.

Expected input:
    - dict or individual arguments: distance, passengers, pickup_hour,
      pickup_zone, dropoff_zone.

Expected output:
    - float: predicted fare amount.

Dependencies:
    - pyspark.ml.PipelineModel
    - A running/local SparkSession (reuse the one from config, or create a
      lightweight one dedicated to inference)

Consumed by:
    - dashboard/pages/4_prediction.py
"""

# TODO: def predict_fare(distance, passengers, pickup_hour, pickup_zone, dropoff_zone) -> float: ...
