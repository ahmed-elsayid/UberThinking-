"""
transforms.py
-------------
The ride schema and the cleaning / feature-engineering step, shared by the
streaming job and the model training script so both see identical columns.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from config import ZONE_LOOKUP_PATH

# Schema of the ride files read by Structured Streaming. Structured Streaming
# can't infer a schema, so we state it explicitly. The integer columns use
# LongType (64-bit) because that's what both pandas and the raw NYC Parquet
# files write, so dropped .parquet files load without a type-conversion error.
RIDE_SCHEMA = StructType(
    [
        StructField("pickup_datetime", StringType(), True),
        StructField("dropoff_datetime", StringType(), True),
        StructField("trip_distance", DoubleType(), True),
        StructField("pickup_location_id", LongType(), True),
        StructField("dropoff_location_id", LongType(), True),
        StructField("fare_amount", DoubleType(), True),
        StructField("tip_amount", DoubleType(), True),
        StructField("passenger_count", LongType(), True),
        StructField("payment_type", StringType(), True),
    ]
)


def clean_and_engineer(df: DataFrame, spark: SparkSession) -> DataFrame:
    """Drops bad rows and adds the derived columns used everywhere downstream.

    Adds: ride_duration_minutes, pickup_hour, and human-readable
    pickup_zone / dropoff_zone (joined from the taxi zone lookup).
    """
    # Keep only rows with valid, positive core values.
    df = (
        df.dropna(subset=["pickup_datetime", "dropoff_datetime", "fare_amount", "trip_distance"])
        .filter(F.col("fare_amount") > 0)
        .filter(F.col("trip_distance") > 0)
    )

    # Parse the timestamp strings; drop rows that fail to parse.
    df = df.withColumn("pickup_datetime", F.to_timestamp("pickup_datetime")).withColumn(
        "dropoff_datetime", F.to_timestamp("dropoff_datetime")
    )
    df = df.dropna(subset=["pickup_datetime", "dropoff_datetime"])

    # Derived columns.
    df = df.withColumn(
        "ride_duration_minutes",
        (F.unix_timestamp("dropoff_datetime") - F.unix_timestamp("pickup_datetime")) / 60.0,
    ).filter(F.col("ride_duration_minutes") > 0)

    df = df.withColumn("pickup_hour", F.hour("pickup_datetime"))

    # Attach readable zone names from the lookup file.
    zones = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(ZONE_LOOKUP_PATH)
    )
    pickup_zones = zones.select(
        F.col("LocationID").alias("pickup_location_id"),
        F.col("Zone").alias("pickup_zone"),
    )
    dropoff_zones = zones.select(
        F.col("LocationID").alias("dropoff_location_id"),
        F.col("Zone").alias("dropoff_zone"),
    )
    df = df.join(pickup_zones, on="pickup_location_id", how="left")
    df = df.join(dropoff_zones, on="dropoff_location_id", how="left")

    return df
