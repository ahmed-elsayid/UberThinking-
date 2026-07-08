"""
analytics.py
------------
Computes the streaming aggregations that power the dashboard's "Overview"
and "Streaming Monitor" pages. Each function is small and composable so it
can be used independently in the streaming job or in unit tests.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def total_revenue(df: DataFrame) -> DataFrame:
    """SUM(fare_amount) as a single-row DataFrame."""
    return df.agg(F.sum("fare_amount").alias("total_revenue"))


def total_trips(df: DataFrame) -> DataFrame:
    """COUNT(*) as a single-row DataFrame."""
    return df.agg(F.count(F.lit(1)).alias("total_trips"))


def average_fare(df: DataFrame) -> DataFrame:
    """AVG(fare_amount) as a single-row DataFrame."""
    return df.agg(F.avg("fare_amount").alias("average_fare"))


def average_duration(df: DataFrame) -> DataFrame:
    """AVG(ride_duration_minutes) as a single-row DataFrame."""
    return df.agg(F.avg("ride_duration_minutes").alias("average_duration_minutes"))


def top_pickup_zones(df: DataFrame, n: int = 10) -> DataFrame:
    """Top n pickup zones by ride count, descending."""
    return (
        df.groupBy("pickup_zone")
        .agg(F.count(F.lit(1)).alias("trip_count"))
        .orderBy(F.desc("trip_count"))
        .limit(n)
    )


def top_dropoff_zones(df: DataFrame, n: int = 10) -> DataFrame:
    """Top n dropoff zones by ride count, descending."""
    return (
        df.groupBy("dropoff_zone")
        .agg(F.count(F.lit(1)).alias("trip_count"))
        .orderBy(F.desc("trip_count"))
        .limit(n)
    )


def payment_distribution(df: DataFrame) -> DataFrame:
    """Ride count grouped by payment_type."""
    return df.groupBy("payment_type").agg(F.count(F.lit(1)).alias("trip_count"))


def trips_by_hour(df: DataFrame) -> DataFrame:
    """Ride count grouped by pickup_hour, ordered by hour (peak-hour analysis)."""
    return (
        df.groupBy("pickup_hour")
        .agg(F.count(F.lit(1)).alias("trip_count"))
        .orderBy("pickup_hour")
    )


def trips_per_window(df: DataFrame, window_duration: str = "5 minutes") -> DataFrame:
    """Windowed trip counts bucketed on pickup_datetime."""
    return (
        df.groupBy(F.window("pickup_datetime", window_duration))
        .agg(F.count(F.lit(1)).alias("trip_count"))
        .orderBy("window")
    )


def compute_aggregations(df: DataFrame, top_n: int = 10) -> dict:
    """Convenience helper bundling every aggregation into a single dict,
    keyed by metric name, so callers (e.g. the streaming consumer) can
    write each one to its own sink.
    """
    return {
        "total_revenue": total_revenue(df),
        "total_trips": total_trips(df),
        "average_fare": average_fare(df),
        "average_duration": average_duration(df),
        "top_pickup_zones": top_pickup_zones(df, top_n),
        "top_dropoff_zones": top_dropoff_zones(df, top_n),
        "payment_distribution": payment_distribution(df),
        "trips_by_hour": trips_by_hour(df),
        "trips_per_window": trips_per_window(df),
    }


