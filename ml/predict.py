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

"""
predict.py
----------
Loads the trained fare-prediction PipelineModel and exposes a simple
function the Streamlit dashboard can call to predict a fare from
user-provided inputs.

Consumed by:
    - dashboard/pages/4_prediction.py
"""

from functools import lru_cache

from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession

from config.config import MODEL_PATH, SPARK_APP_NAME, SPARK_MASTER

# A ride hasn't happened yet at prediction time, so duration is unknown.
# We estimate it from an assumed average city-driving speed so the same
# feature columns used at training time (ride_duration_minutes) can still
# be populated for inference.
_ASSUMED_AVERAGE_SPEED_MPH = 15.0
_DEFAULT_PAYMENT_TYPE = "Card"


@lru_cache(maxsize=1)
def _get_spark() -> SparkSession:
    return SparkSession.builder.appName(f"{SPARK_APP_NAME}-Predict").master(SPARK_MASTER).getOrCreate()


@lru_cache(maxsize=1)
def _get_model() -> PipelineModel:
    """Loads the saved PipelineModel once and caches it for the process
    lifetime, avoiding a reload on every prediction request.
    """
    return PipelineModel.load(MODEL_PATH)


def predict_fare(
    distance: float,
    passengers: int,
    pickup_hour: int,
    pickup_zone: str,
    dropoff_zone: str,
) -> float:
    """Predicts a fare amount for a ride that hasn't started yet.

    Args:
        distance: Estimated trip distance, in miles.
        passengers: Number of passengers.
        pickup_hour: Hour of day (0-23) the ride will start.
        pickup_zone: Pickup zone name (must match a zone seen in training).
        dropoff_zone: Dropoff zone name (must match a zone seen in training).

    Returns:
        Predicted fare amount as a plain Python float.
    """
    spark = _get_spark()
    model = _get_model()

    estimated_duration_minutes = (distance / _ASSUMED_AVERAGE_SPEED_MPH) * 60.0

    row = {
        "trip_distance": float(distance),
        "passenger_count": int(passengers),
        "pickup_hour": int(pickup_hour),
        "pickup_zone": pickup_zone,
        "dropoff_zone": dropoff_zone,
        "ride_duration_minutes": float(estimated_duration_minutes),
        "payment_type": _DEFAULT_PAYMENT_TYPE,
    }

    input_df = spark.createDataFrame([row])
    prediction_row = model.transform(input_df).select("predicted_fare").first()

    return float(prediction_row["predicted_fare"])
