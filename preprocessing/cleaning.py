"""
cleaning.py
-----------
Purpose:
    Cleans raw parsed ride records and engineers derived features used by
    both streaming analytics and the ML model. Shared by the streaming
    consumer (real-time) and, if desired, batch/offline training scripts.

Responsibilities:
    - Remove/flag invalid records:
        - null critical fields (pickup/dropoff time, fare, distance)
        - negative or zero fare_amount / trip_distance
        - duplicate rides (if an identifiable ride key exists)
    - Cast string datetimes to TimestampType.
    - Join pickup/dropoff LocationID onto zone/borough names using
      data/zone_lookup/taxi_zone_lookup.csv.
    - Derive new columns:
        - ride_duration_minutes  (dropoff - pickup)
        - average_speed_mph      (trip_distance / ride_duration)
        - pickup_hour, pickup_day, pickup_month, pickup_weekday
        - is_weekend (boolean)

Expected input:
    - Spark DataFrame matching streaming/schema.py (RIDE_SCHEMA), either
      streaming or static/batch.

Expected output:
    - Spark DataFrame with all original + derived columns, invalid rows
      removed.

Dependencies:
    - pyspark.sql.functions (to_timestamp, col, when, unix_timestamp, etc.)
    - data/zone_lookup/taxi_zone_lookup.csv

Consumed by:
    - streaming/spark_stream_consumer.py
    - ml/train_model.py (for building training features)
"""

# TODO: def clean_and_engineer(df): ... return cleaned_df
