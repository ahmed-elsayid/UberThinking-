"""
test_analytics.py
-------------------
Unit tests for analytics/analytics.py — verifies streaming aggregation
functions produce correct results on small, known sample DataFrames.
"""

import pytest
from pyspark.sql import Row, SparkSession

from analytics.analytics import (
    average_duration,
    average_fare,
    payment_distribution,
    top_pickup_zones,
    total_revenue,
    total_trips,
    trips_by_hour,
    trips_per_window,
)


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.appName("test_analytics")
        .master("local[1]")
        .getOrCreate()
    )
    yield session
    session.stop()


@pytest.fixture(scope="module")
def sample_df(spark):
    rows = [
        Row(
            pickup_datetime="2024-05-01 10:00:00",
            fare_amount=10.0,
            ride_duration_minutes=15.0,
            pickup_zone="Zone A",
            dropoff_zone="Zone B",
            payment_type="Card",
            pickup_hour=10,
        ),
        Row(
            pickup_datetime="2024-05-01 10:02:00",
            fare_amount=20.0,
            ride_duration_minutes=25.0,
            pickup_zone="Zone A",
            dropoff_zone="Zone C",
            payment_type="Cash",
            pickup_hour=10,
        ),
        Row(
            pickup_datetime="2024-05-01 11:00:00",
            fare_amount=30.0,
            ride_duration_minutes=10.0,
            pickup_zone="Zone B",
            dropoff_zone="Zone B",
            payment_type="Card",
            pickup_hour=11,
        ),
    ]
    df = spark.createDataFrame(rows)
    return df.withColumn("pickup_datetime", df["pickup_datetime"].cast("timestamp"))


def test_total_revenue_sums_fares(sample_df):
    result = total_revenue(sample_df).first()
    assert result["total_revenue"] == pytest.approx(60.0)


def test_total_trips_counts_rows(sample_df):
    result = total_trips(sample_df).first()
    assert result["total_trips"] == 3


def test_average_fare_and_duration(sample_df):
    fare_result = average_fare(sample_df).first()
    duration_result = average_duration(sample_df).first()
    assert fare_result["average_fare"] == pytest.approx(20.0)
    assert duration_result["average_duration_minutes"] == pytest.approx(50.0 / 3)


def test_top_pickup_zones_ordering(sample_df):
    rows = top_pickup_zones(sample_df, n=2).collect()
    assert rows[0]["pickup_zone"] == "Zone A"
    assert rows[0]["trip_count"] == 2


def test_payment_distribution_grouping(sample_df):
    rows = {r["payment_type"]: r["trip_count"] for r in payment_distribution(sample_df).collect()}
    assert rows["Card"] == 2
    assert rows["Cash"] == 1


def test_trips_by_hour_grouping(sample_df):
    rows = {r["pickup_hour"]: r["trip_count"] for r in trips_by_hour(sample_df).collect()}
    assert rows[10] == 2
    assert rows[11] == 1


def test_trips_per_window_bucketing(sample_df):
    rows = trips_per_window(sample_df, "5 minutes").collect()
    total = sum(r["trip_count"] for r in rows)
    assert total == 3
    # The two 10:00/10:02 rides should fall in the same 5-minute window.
    assert any(r["trip_count"] == 2 for r in rows)
