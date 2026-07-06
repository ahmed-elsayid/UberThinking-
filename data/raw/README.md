# data/raw/

Purpose:
    Holds the historical NYC Taxi dataset that the Kafka producer replays
    as a simulated real-time feed. This folder is gitignored — do not
    commit large data files to the repository.

What goes here:
    - One or more NYC TLC "Yellow Taxi Trip Records" files (Parquet or CSV),
      downloadable from the official NYC TLC Trip Record Data page.

Expected columns (subset relevant to this project):
    - tpep_pickup_datetime / tpep_dropoff_datetime
    - trip_distance
    - PULocationID / DOLocationID   (see data/zone_lookup/)
    - fare_amount
    - tip_amount
    - passenger_count
    - payment_type

Setup steps (to perform, not implement):
    1. Download one month of Yellow Taxi trip data.
    2. Place the file(s) in this folder.
    3. Point RAW_DATA_PATH in `.env` to the file location.

Note:
    Consider using a single month (or a sampled subset) for development —
    full datasets contain millions of rows and are not needed to demo
    streaming behavior.
