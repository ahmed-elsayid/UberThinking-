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
