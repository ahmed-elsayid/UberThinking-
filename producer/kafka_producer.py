"""
kafka_producer.py
------------------
Purpose:
    Reads historical taxi ride rows from data/raw/ and streams them, one
    at a time, to a Kafka topic — simulating a live feed of taxi rides
    arriving in real time (rather than replaying the whole dataset at once).

Responsibilities:
    - Read rows sequentially from the raw dataset (e.g., via pandas or a
      simple file iterator — this file should NOT depend on Spark).
    - Convert each row into a JSON message matching the schema expected by
      streaming/schema.py.
    - Publish each JSON message to the Kafka topic named in config
      (KAFKA_TOPIC).
    - Sleep for PRODUCER_DELAY_SECONDS between messages to simulate
      realistic ride arrival timing.
    - Handle basic errors (e.g., malformed rows) by logging and skipping.

Expected input:
    - File at RAW_DATA_PATH (see config/config.py).

Expected output:
    - JSON messages published to Kafka topic KAFKA_TOPIC, e.g.:
        {
          "pickup_datetime": "2024-05-01T10:05:00",
          "dropoff_datetime": "2024-05-01T10:21:00",
          "trip_distance": 6.5,
          "pickup_location_id": 142,
          "dropoff_location_id": 236,
          "fare_amount": 18.3,
          "tip_amount": 3.2,
          "passenger_count": 2,
          "payment_type": "Card"
        }

Dependencies:
    - kafka-python (KafkaProducer)
    - pandas (or csv/pyarrow) for reading raw data
    - config/config.py

Run:
    python producer/kafka_producer.py
"""

# TODO: implement producer loop:
#   1. Load config.
#   2. Open raw data file as an iterator.
#   3. For each row -> build dict -> json.dumps -> producer.send(topic, value)
#   4. time.sleep(PRODUCER_DELAY_SECONDS)


"""
kafka_producer.py
------------------
Reads historical taxi ride rows from data/raw/ and streams them, one at a
time, to a Kafka topic — simulating a live feed of taxi rides arriving in
real time. Deliberately Spark-free; uses pandas for reading and
kafka-python for publishing.

Run:
    python producer/kafka_producer.py
"""

import json
import logging
import time
from typing import Iterator

import pandas as pd
from kafka import KafkaProducer

from config.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    PRODUCER_DELAY_SECONDS,
    RAW_DATA_PATH,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# NYC TLC's numeric payment_type codes -> human-readable labels used
# downstream by streaming/schema.py's payment_type (StringType) field.
PAYMENT_TYPE_LABELS = {
    1: "Card",
    2: "Cash",
    3: "No Charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided Trip",
}

# Maps a TLC source column name to the JSON key expected by the consumer.
_COLUMN_ALIASES = {
    "tpep_pickup_datetime": "pickup_datetime",
    "pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "dropoff_datetime": "dropoff_datetime",
    "trip_distance": "trip_distance",
    "PULocationID": "pickup_location_id",
    "pickup_location_id": "pickup_location_id",
    "DOLocationID": "dropoff_location_id",
    "dropoff_location_id": "dropoff_location_id",
    "fare_amount": "fare_amount",
    "tip_amount": "tip_amount",
    "passenger_count": "passenger_count",
    "payment_type": "payment_type",
}


def _read_raw_rows(path: str) -> Iterator[dict]:
    """Reads the raw dataset (Parquet or CSV) and yields one dict per row,
    with keys already normalized to the producer's JSON schema.
    """
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)

    # Keep only known columns, renamed to the target JSON keys.
    rename_map = {c: _COLUMN_ALIASES[c] for c in df.columns if c in _COLUMN_ALIASES}
    df = df.rename(columns=rename_map)
    df = df[[c for c in _COLUMN_ALIASES.values() if c in df.columns]]

    for _, row in df.iterrows():
        yield row.to_dict()


def _build_message(row: dict) -> dict:
    """Converts a raw row dict into the JSON message shape expected by
    streaming/schema.py, coercing types and normalizing payment_type.
    """
    pickup_dt = row.get("pickup_datetime")
    dropoff_dt = row.get("dropoff_datetime")

    payment_type = row.get("payment_type")
    if isinstance(payment_type, (int, float)) and not pd.isna(payment_type):
        payment_type = PAYMENT_TYPE_LABELS.get(int(payment_type), "Unknown")
    elif payment_type is None or (isinstance(payment_type, float) and pd.isna(payment_type)):
        payment_type = "Unknown"
    else:
        payment_type = str(payment_type)

    return {
        "pickup_datetime": str(pd.Timestamp(pickup_dt)) if pickup_dt is not None else None,
        "dropoff_datetime": str(pd.Timestamp(dropoff_dt)) if dropoff_dt is not None else None,
        "trip_distance": float(row["trip_distance"]) if not pd.isna(row.get("trip_distance")) else None,
        "pickup_location_id": int(row["pickup_location_id"]) if not pd.isna(row.get("pickup_location_id")) else None,
        "dropoff_location_id": int(row["dropoff_location_id"]) if not pd.isna(row.get("dropoff_location_id")) else None,
        "fare_amount": float(row["fare_amount"]) if not pd.isna(row.get("fare_amount")) else None,
        "tip_amount": float(row["tip_amount"]) if not pd.isna(row.get("tip_amount")) else 0.0,
        "passenger_count": int(row["passenger_count"]) if not pd.isna(row.get("passenger_count")) else None,
        "payment_type": payment_type,
    }


def run(
    raw_data_path: str = RAW_DATA_PATH,
    topic: str = KAFKA_TOPIC,
    bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS,
    delay_seconds: float = PRODUCER_DELAY_SECONDS,
) -> None:
    """Streams rows from `raw_data_path` to `topic`, one message every
    `delay_seconds`, simulating a live feed of arriving taxi rides.
    """
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    sent, skipped = 0, 0
    try:
        for row in _read_raw_rows(raw_data_path):
            try:
                message = _build_message(row)
                producer.send(topic, value=message)
                sent += 1
            except Exception as exc:  # malformed row: log and continue
                skipped += 1
                logger.warning("Skipping malformed row (%s): %s", exc, row)
                continue

            time.sleep(delay_seconds)
    finally:
        producer.flush()
        producer.close()
        logger.info("Producer finished. Sent=%d Skipped=%d", sent, skipped)


if __name__ == "__main__":
    run()
