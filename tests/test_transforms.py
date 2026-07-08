"""
test_transforms.py
------------------
A small test for clean_and_engineer: bad rows are dropped and the derived
columns are added correctly.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import pytest
from pyspark.sql import Row, SparkSession

from transforms import clean_and_engineer


@pytest.fixture(scope="module")
def spark():
    session = SparkSession.builder.appName("test").master("local[1]").getOrCreate()
    yield session
    session.stop()


def test_cleaning_drops_bad_rows_and_adds_features(spark):
    rows = [
        # good ride: 20 minutes long, 3 miles, $15
        Row(
            pickup_datetime="2020-01-01 10:00:00",
            dropoff_datetime="2020-01-01 10:20:00",
            trip_distance=3.0,
            pickup_location_id=1,
            dropoff_location_id=2,
            fare_amount=15.0,
            tip_amount=2.0,
            passenger_count=1,
            payment_type="Card",
        ),
        # bad ride: negative fare -> should be dropped
        Row(
            pickup_datetime="2020-01-01 11:00:00",
            dropoff_datetime="2020-01-01 11:10:00",
            trip_distance=2.0,
            pickup_location_id=1,
            dropoff_location_id=2,
            fare_amount=-5.0,
            tip_amount=0.0,
            passenger_count=1,
            payment_type="Cash",
        ),
    ]
    result = clean_and_engineer(spark.createDataFrame(rows), spark)

    collected = result.collect()
    assert len(collected) == 1  # bad row dropped

    ride = collected[0]
    assert ride["ride_duration_minutes"] == pytest.approx(20.0)
    assert ride["pickup_hour"] == 10
