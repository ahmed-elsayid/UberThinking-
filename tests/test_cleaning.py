"""
test_cleaning.py
-----------------
Purpose:
    Unit tests for preprocessing/cleaning.py — verifies that invalid rows
    are removed and derived columns are computed correctly.

Suggested test cases:
    - test_removes_null_critical_fields: rows missing pickup/dropoff time,
      fare, or distance are dropped.
    - test_removes_negative_fare: rows with fare_amount < 0 are dropped.
    - test_removes_negative_distance: rows with trip_distance < 0 are dropped.
    - test_removes_duplicate_rides: exact duplicate rows are deduplicated.
    - test_ride_duration_calculation: ride_duration_minutes matches
      (dropoff - pickup) in minutes for a known input.
    - test_average_speed_calculation: average_speed_mph matches
      distance / duration for a known input.
    - test_pickup_hour_and_weekend_flags: pickup_hour, is_weekend derived
      correctly from a known pickup_datetime.

Dependencies:
    - pytest
    - pyspark (a local SparkSession fixture, scope="module")
"""

# TODO: implement fixtures + test functions described above.


"""
test_cleaning.py
-----------------
Unit tests for preprocessing/cleaning.py — verifies that invalid rows are
removed and derived columns are computed correctly.
"""

import os
import tempfile

import pytest
from pyspark.sql import Row, SparkSession

from preprocessing.cleaning import clean_and_engineer


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.appName("test_cleaning")
        .master("local[1]")
        .getOrCreate()
    )
    yield session
    session.stop()


@pytest.fixture(scope="module")
def zone_lookup_path():
    """Writes a tiny zone lookup CSV so joins in clean_and_engineer work
    without depending on the real (gitignored) dataset.
    """
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "taxi_zone_lookup.csv")
    with open(path, "w") as f:
        f.write("LocationID,Borough,Zone,service_zone\n")
        f.write("1,Manhattan,Zone A,Yellow Zone\n")
        f.write("2,Brooklyn,Zone B,Boro Zone\n")
    return path


def _make_rows(spark, rows):
    return spark.createDataFrame([Row(**r) for r in rows])


BASE_ROW = {
    "pickup_datetime": "2024-05-01 10:00:00",
    "dropoff_datetime": "2024-05-01 10:16:00",
    "trip_distance": 5.0,
    "pickup_location_id": 1,
    "dropoff_location_id": 2,
    "fare_amount": 20.0,
    "tip_amount": 2.0,
    "passenger_count": 1,
    "payment_type": "Card",
}


def test_removes_null_critical_fields(spark, zone_lookup_path):
    rows = [dict(BASE_ROW, pickup_datetime=None)]
    df = _make_rows(spark, rows)
    result = clean_and_engineer(df, spark=spark, zone_lookup_path=zone_lookup_path)
    assert result.count() == 0


def test_removes_negative_fare(spark, zone_lookup_path):
    rows = [dict(BASE_ROW, fare_amount=-5.0)]
    df = _make_rows(spark, rows)
    result = clean_and_engineer(df, spark=spark, zone_lookup_path=zone_lookup_path)
    assert result.count() == 0


def test_removes_negative_distance(spark, zone_lookup_path):
    rows = [dict(BASE_ROW, trip_distance=-1.0)]
    df = _make_rows(spark, rows)
    result = clean_and_engineer(df, spark=spark, zone_lookup_path=zone_lookup_path)
    assert result.count() == 0


def test_removes_duplicate_rides(spark, zone_lookup_path):
    rows = [dict(BASE_ROW), dict(BASE_ROW)]
    df = _make_rows(spark, rows)
    result = clean_and_engineer(df, spark=spark, zone_lookup_path=zone_lookup_path)
    assert result.count() == 1


def test_ride_duration_calculation(spark, zone_lookup_path):
    df = _make_rows(spark, [dict(BASE_ROW)])
    result = clean_and_engineer(df, spark=spark, zone_lookup_path=zone_lookup_path)
    duration = result.select("ride_duration_minutes").first()["ride_duration_minutes"]
    assert duration == pytest.approx(16.0)


def test_average_speed_calculation(spark, zone_lookup_path):
    df = _make_rows(spark, [dict(BASE_ROW)])
    result = clean_and_engineer(df, spark=spark, zone_lookup_path=zone_lookup_path)
    row = result.first()
    expected_speed = row["trip_distance"] / (row["ride_duration_minutes"] / 60.0)
    assert row["average_speed_mph"] == pytest.approx(expected_speed)


def test_pickup_hour_and_weekend_flags(spark, zone_lookup_path):
    # 2024-05-01 is a Wednesday -> not a weekend.
    df = _make_rows(spark, [dict(BASE_ROW)])
    result = clean_and_engineer(df, spark=spark, zone_lookup_path=zone_lookup_path)
    row = result.first()
    assert row["pickup_hour"] == 10
    assert row["is_weekend"] is False
