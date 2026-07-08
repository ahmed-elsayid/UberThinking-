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

import glob
import json
import logging
import os
import time
from typing import Iterator, List

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

# Target JSON keys a source file must provide (after aliasing) to be usable
# by the downstream pipeline. A file whose columns don't cover all of these
# is skipped rather than streamed as mostly-null rows. (e.g. the pre-2016
# TLC schema has no LocationID columns and is skipped here.)
_REQUIRED_COLUMNS = [
    "pickup_datetime",
    "dropoff_datetime",
    "trip_distance",
    "fare_amount",
    "pickup_location_id",
    "dropoff_location_id",
    "passenger_count",
    "payment_type",
]

# Supported raw file extensions when scanning a directory.
_SUPPORTED_EXTENSIONS = (".parquet", ".csv")


def _iter_source_files(path: str) -> List[str]:
    """Returns the raw data files to read.

    If `path` is a directory, returns every supported (.parquet/.csv) file
    inside it, searched recursively and sorted for deterministic order. If
    `path` is a single file, returns just that file.
    """
    if os.path.isdir(path):
        files: List[str] = []
        for ext in _SUPPORTED_EXTENSIONS:
            files.extend(glob.glob(os.path.join(path, "**", f"*{ext}"), recursive=True))
        return sorted(files)
    return [path]


def _source_columns(path: str) -> List[str]:
    """Returns the column names of a raw file cheaply, without loading all
    rows (reads Parquet metadata / only the CSV header).
    """
    if path.endswith(".parquet"):
        import pyarrow.parquet as pq

        return list(pq.ParquetFile(path).schema_arrow.names)
    return list(pd.read_csv(path, nrows=0).columns)


def _fits_requirements(source_columns: List[str]) -> bool:
    """True if a file's columns, once aliased, cover every required column."""
    aliased = {_COLUMN_ALIASES[c] for c in source_columns if c in _COLUMN_ALIASES}
    return all(col in aliased for col in _REQUIRED_COLUMNS)


def _normalize_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Renames source columns to the producer's JSON keys and keeps only the
    known target columns (deduplicated, since several source names can alias
    to the same target).
    """
    rename_map = {c: _COLUMN_ALIASES[c] for c in df.columns if c in _COLUMN_ALIASES}
    df = df.rename(columns=rename_map)
    target_cols = list(dict.fromkeys(_COLUMN_ALIASES.values()))
    return df[[c for c in target_cols if c in df.columns]]


def _read_file_rows(path: str) -> Iterator[dict]:
    """Yields normalized row dicts from a single Parquet/CSV file, reading
    Parquet in batches to keep memory bounded on large files.
    """
    if path.endswith(".parquet"):
        import pyarrow.parquet as pq

        parquet_file = pq.ParquetFile(path)
        for batch in parquet_file.iter_batches(batch_size=1000):
            df = _normalize_frame(batch.to_pandas())
            for _, row in df.iterrows():
                yield row.to_dict()
    else:
        df = _normalize_frame(pd.read_csv(path))
        for _, row in df.iterrows():
            yield row.to_dict()


def _read_raw_rows(path: str) -> Iterator[dict]:
    """Reads the raw data source (a single Parquet/CSV file, or a directory
    containing many of them) and yields one dict per row, normalized to the
    producer's JSON schema. Files whose schema doesn't meet the required
    columns are logged and skipped.
    """
    files = _iter_source_files(path)
    if not files:
        logger.warning("No .parquet/.csv files found at %s", path)
        return

    used = 0
    for file_path in files:
        try:
            columns = _source_columns(file_path)
        except Exception as exc:
            logger.warning("Skipping unreadable file %s: %s", file_path, exc)
            continue

        if not _fits_requirements(columns):
            missing = [
                c
                for c in _REQUIRED_COLUMNS
                if c not in {_COLUMN_ALIASES[s] for s in columns if s in _COLUMN_ALIASES}
            ]
            logger.warning("Skipping %s: missing required columns %s", file_path, missing)
            continue

        used += 1
        logger.info("Streaming rows from %s", file_path)
        yield from _read_file_rows(file_path)

    logger.info("Used %d of %d source file(s) under %s", used, len(files), path)


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
