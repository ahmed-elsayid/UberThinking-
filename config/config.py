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
