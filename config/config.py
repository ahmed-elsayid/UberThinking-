"""
config.py
---------
Purpose:
    Single source of truth for all environment-dependent settings
    (Kafka connection info, file paths, Spark app name, producer timing,
    etc.). Every other module should import from here instead of
    hardcoding values or reading os.environ directly.

Responsibilities:
    - Load variables from a `.env` file (via python-dotenv) at import time.
    - Expose typed, named constants/config objects to the rest of the app.
    - Provide sensible defaults for local development.

Expected contents (to implement):
    - KAFKA_BOOTSTRAP_SERVERS: str
    - KAFKA_TOPIC: str
    - SPARK_MASTER: str
    - SPARK_APP_NAME: str
    - RAW_DATA_PATH: str
    - ZONE_LOOKUP_PATH: str
    - CHECKPOINT_PATH: str
    - PARQUET_OUTPUT_PATH: str
    - MODEL_PATH: str
    - PRODUCER_DELAY_SECONDS: float

Dependencies:
    - python-dotenv
    - os (standard library)

Consumed by:
    - producer/kafka_producer.py
    - streaming/spark_stream_consumer.py
    - analytics/analytics.py
    - ml/train_model.py, ml/predict.py
    - dashboard/app.py and its pages
"""

# TODO: load_dotenv() and define config constants here.


"""
config.py
---------
Single source of truth for all environment-dependent settings (Kafka
connection info, file paths, Spark app name, producer timing, etc.).
Every other module imports from here instead of hardcoding values or
reading os.environ directly.
"""

import os

from dotenv import load_dotenv

# Load variables from a .env file in the project root (if present).
# Falls back to already-exported environment variables / defaults below.
load_dotenv()


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# --- Kafka ---
KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "taxi_rides")

# --- Spark ---
SPARK_MASTER: str = os.getenv("SPARK_MASTER", "local[*]")
SPARK_APP_NAME: str = os.getenv("SPARK_APP_NAME", "UberThinking")

# --- File paths ---
RAW_DATA_PATH: str = os.getenv("RAW_DATA_PATH", "data/raw/taxi_data.parquet")
ZONE_LOOKUP_PATH: str = os.getenv("ZONE_LOOKUP_PATH", "data/zone_lookup/taxi_zone_lookup.csv")
CHECKPOINT_PATH: str = os.getenv("CHECKPOINT_PATH", "output/checkpoints/")
PARQUET_OUTPUT_PATH: str = os.getenv("PARQUET_OUTPUT_PATH", "output/parquet/")
MODEL_PATH: str = os.getenv("MODEL_PATH", "models/fare_prediction")

# Derived, commonly used sub-paths under PARQUET_OUTPUT_PATH.
RIDES_OUTPUT_PATH: str = os.path.join(PARQUET_OUTPUT_PATH, "rides")
AGGREGATES_OUTPUT_PATH: str = os.path.join(PARQUET_OUTPUT_PATH, "aggregates")
RIDES_CHECKPOINT_PATH: str = os.path.join(CHECKPOINT_PATH, "rides")
AGGREGATES_CHECKPOINT_PATH: str = os.path.join(CHECKPOINT_PATH, "aggregates")

# --- Producer behavior ---
PRODUCER_DELAY_SECONDS: float = _get_float("PRODUCER_DELAY_SECONDS", 0.5)
