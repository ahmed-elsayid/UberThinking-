# data/raw/

Put the historical NYC taxi dataset here. This folder is gitignored — don't
commit large data files.

**What goes here:** one NYC TLC "Yellow Taxi Trip Records" Parquet file,
e.g. `yellow_tripdata_2020-01.parquet`, downloadable from the official NYC
TLC Trip Record Data page.

This file is used two ways:
1. `src/generate_stream.py` reads it and replays rows as a simulated live feed.
2. `src/train_model.py` trains the fare-prediction model on it.

Expected columns: `tpep_pickup_datetime`, `tpep_dropoff_datetime`,
`trip_distance`, `PULocationID`, `DOLocationID`, `fare_amount`, `tip_amount`,
`passenger_count`, `payment_type`.
