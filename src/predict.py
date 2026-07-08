"""
predict.py
----------
Loads the trained model and predicts a fare from user inputs. Used by the
dashboard's Prediction page.
"""

from functools import lru_cache

from config import MODEL_PATH, build_spark

# The ride hasn't happened yet, so we estimate its duration from an assumed
# average speed to fill the ride_duration_minutes feature.
ASSUMED_SPEED_MPH = 15.0


@lru_cache(maxsize=1)
def _spark():
    return build_spark("UberThinking-Predict")


@lru_cache(maxsize=1)
def _model():
    from pyspark.ml import PipelineModel

    return PipelineModel.load(MODEL_PATH)


def predict_fare(distance, passengers, pickup_hour, pickup_zone, dropoff_zone) -> float:
    """Returns the predicted fare (in dollars) for a not-yet-started ride."""
    spark = _spark()
    estimated_duration = (distance / ASSUMED_SPEED_MPH) * 60.0

    row = {
        "trip_distance": float(distance),
        "passenger_count": int(passengers),
        "pickup_hour": int(pickup_hour),
        "ride_duration_minutes": float(estimated_duration),
        "pickup_zone": pickup_zone,
        "dropoff_zone": dropoff_zone,
    }
    result = _model().transform(spark.createDataFrame([row]))
    return float(result.select("predicted_fare").first()["predicted_fare"])
