"""
generate_stream.py
------------------
Simulates a live feed WITHOUT Kafka. It reads the historical NYC taxi
dataset and drops small Parquet files into data/stream/ every couple of
seconds. Spark Structured Streaming watches that folder (see
streaming_job.py) and picks up each new file as it appears.

You can also drop your own .csv or .parquet files into data/stream/ by hand
(with the same columns as row_to_message below) and the streaming job will
pick them up too.

Run:
    python src/generate_stream.py
"""

import glob
import os
import time

import pandas as pd

from config import (
    HISTORICAL_DATA_PATH,
    STREAM_BATCH_SIZE,
    STREAM_DELAY_SECONDS,
    STREAM_INPUT_PATH,
)

# NYC TLC numeric payment codes -> readable labels.
PAYMENT_LABELS = {1: "Card", 2: "Cash", 3: "No Charge", 4: "Dispute", 5: "Unknown", 6: "Voided"}


def load_historical() -> pd.DataFrame:
    """Loads the historical dataset (a single .parquet file or a folder)."""
    path = HISTORICAL_DATA_PATH
    if os.path.isdir(path):
        files = sorted(glob.glob(os.path.join(path, "*.parquet")))
        if not files:
            raise FileNotFoundError(f"No .parquet files found in {path}")
        path = files[0]

    df = pd.read_parquet(path)

    # Rename TLC columns to the names our pipeline expects.
    df = df.rename(
        columns={
            "tpep_pickup_datetime": "pickup_datetime",
            "tpep_dropoff_datetime": "dropoff_datetime",
            "PULocationID": "pickup_location_id",
            "DOLocationID": "dropoff_location_id",
        }
    )
    keep = [
        "pickup_datetime",
        "dropoff_datetime",
        "trip_distance",
        "pickup_location_id",
        "dropoff_location_id",
        "fare_amount",
        "tip_amount",
        "passenger_count",
        "payment_type",
    ]
    return df[[c for c in keep if c in df.columns]]


def row_to_message(row: pd.Series) -> dict:
    """Turns one dataframe row into a clean dict with our standard columns."""
    payment = row.get("payment_type")
    payment = PAYMENT_LABELS.get(int(payment), "Unknown") if pd.notna(payment) else "Unknown"
    return {
        "pickup_datetime": str(row["pickup_datetime"]),
        "dropoff_datetime": str(row["dropoff_datetime"]),
        "trip_distance": float(row["trip_distance"]),
        "pickup_location_id": int(row["pickup_location_id"]),
        "dropoff_location_id": int(row["dropoff_location_id"]),
        "fare_amount": float(row["fare_amount"]),
        "tip_amount": float(row["tip_amount"]) if pd.notna(row.get("tip_amount")) else 0.0,
        "passenger_count": int(row["passenger_count"]) if pd.notna(row.get("passenger_count")) else 1,
        "payment_type": payment,
    }


def main() -> None:
    os.makedirs(STREAM_INPUT_PATH, exist_ok=True)
    df = load_historical()
    print(f"Loaded {len(df):,} historical rides. Writing {STREAM_BATCH_SIZE} per file...")

    batch_number = 0
    for start in range(0, len(df), STREAM_BATCH_SIZE):
        batch = df.iloc[start : start + STREAM_BATCH_SIZE]
        messages = []
        for _, row in batch.iterrows():
            try:
                messages.append(row_to_message(row))
            except (ValueError, TypeError):
                continue  # skip malformed rows

        # Write to a temp name first, then rename, so the streaming job never
        # sees a half-written file.
        out_file = os.path.join(STREAM_INPUT_PATH, f"rides_{batch_number:05d}.parquet")
        tmp_file = out_file + ".tmp"
        pd.DataFrame(messages).to_parquet(tmp_file, index=False)
        os.replace(tmp_file, out_file)

        batch_number += 1
        print(f"Wrote {out_file} ({len(messages)} rides)")
        time.sleep(STREAM_DELAY_SECONDS)

    print("Done streaming all historical rides.")


if __name__ == "__main__":
    main()
