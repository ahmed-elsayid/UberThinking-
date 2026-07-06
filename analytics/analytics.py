"""
analytics.py
------------
Purpose:
    Computes the streaming aggregations that power the dashboard's
    "Overview" and "Streaming Monitor" pages.

Responsibilities (each as a separate, composable function):
    - total_revenue(df)          -> SUM(fare_amount)
    - total_trips(df)            -> COUNT(*)
    - average_fare(df)           -> AVG(fare_amount)
    - average_duration(df)       -> AVG(ride_duration_minutes)
    - top_pickup_zones(df, n)    -> GROUP BY pickup_zone, ORDER BY count DESC
    - top_dropoff_zones(df, n)   -> GROUP BY dropoff_zone, ORDER BY count DESC
    - payment_distribution(df)   -> GROUP BY payment_type
    - trips_by_hour(df)          -> GROUP BY pickup_hour (peak-hour analysis)
    - trips_per_window(df)       -> windowed count using
                                     window("pickup_datetime", "5 minutes")

Expected input:
    - Cleaned Spark DataFrame produced by preprocessing/cleaning.py.

Expected output:
    - One Spark DataFrame per metric (or a dict of DataFrames), ready to be
      written to a sink the dashboard can read.

Dependencies:
    - pyspark.sql.functions (window, sum, count, avg, col, desc)

Consumed by:
    - streaming/spark_stream_consumer.py (to write aggregate sinks)
    - dashboard/pages/1_overview.py, 5_streaming_monitor.py (indirectly,
      via the Parquet/aggregate sink written by the streaming job)
"""

# TODO: implement each aggregation function described above.
