"""
cleaning.py
-----------
Cleans raw parsed ride records and engineers derived features used by both
streaming analytics and the ML model. Shared by the streaming consumer
(real-time) and batch/offline training scripts.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from config.config import ZONE_LOOKUP_PATH

# Critical fields that must be present (non-null) for a ride to be usable.
_CRITICAL_FIELDS = [
    "pickup_datetime",
    "dropoff_datetime",
    "fare_amount",
    "trip_distance",
]


def _load_zone_lookup(spark: SparkSession, zone_lookup_path: str) -> DataFrame:
    """Loads the taxi zone lookup CSV (LocationID, Borough, Zone, service_zone)."""
    return (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(zone_lookup_path)
    )


def clean_and_engineer(
    df: DataFrame,
    spark: SparkSession = None,
    zone_lookup_path: str = None,
) -> DataFrame:
    """Cleans raw ride records and derives feature columns.

    Args:
        df: Spark DataFrame matching streaming/schema.py (RIDE_SCHEMA),
            either streaming or static/batch.
        spark: Active SparkSession, used to load the zone lookup CSV.
            Defaults to the session that created `df` when not provided.
        zone_lookup_path: Path to taxi_zone_lookup.csv. Defaults to
            config.ZONE_LOOKUP_PATH.

    Returns:
        Spark DataFrame with all original + derived columns, invalid rows
        removed.
    """
    spark = spark or df.sparkSession
    zone_lookup_path = zone_lookup_path or ZONE_LOOKUP_PATH

    cleaned = df

    # --- Drop rows with null critical fields ---
    for field in _CRITICAL_FIELDS:
        if field in cleaned.columns:
            cleaned = cleaned.filter(F.col(field).isNotNull())

    # --- Drop non-positive fare_amount / trip_distance ---
    cleaned = cleaned.filter(F.col("fare_amount") > 0)
    cleaned = cleaned.filter(F.col("trip_distance") > 0)

    # --- Cast string datetimes to TimestampType ---
    cleaned = cleaned.withColumn(
        "pickup_datetime", F.to_timestamp(F.col("pickup_datetime"))
    ).withColumn("dropoff_datetime", F.to_timestamp(F.col("dropoff_datetime")))

    # Casting can null out unparsable datetimes; drop those too.
    cleaned = cleaned.filter(
        F.col("pickup_datetime").isNotNull() & F.col("dropoff_datetime").isNotNull()
    )

    # --- Remove duplicate rides (identical on every original field) ---
    cleaned = cleaned.dropDuplicates()

    # --- Derived columns ---
    cleaned = cleaned.withColumn(
        "ride_duration_minutes",
        (
            F.unix_timestamp("dropoff_datetime") - F.unix_timestamp("pickup_datetime")
        )
        / 60.0,
    )

    # Guard against zero/negative duration before computing speed.
    cleaned = cleaned.filter(F.col("ride_duration_minutes") > 0)

    cleaned = cleaned.withColumn(
        "average_speed_mph",
        F.col("trip_distance") / (F.col("ride_duration_minutes") / 60.0),
    )

    cleaned = (
        cleaned.withColumn("pickup_hour", F.hour("pickup_datetime"))
        .withColumn("pickup_day", F.dayofmonth("pickup_datetime"))
        .withColumn("pickup_month", F.month("pickup_datetime"))
        .withColumn("pickup_weekday", F.dayofweek("pickup_datetime"))
        .withColumn(
            "is_weekend",
            F.col("pickup_weekday").isin(1, 7),  # Spark: 1=Sunday, 7=Saturday
        )
    )

    # --- Join zone/borough names onto pickup/dropoff location IDs ---
    try:
        zone_lookup = _load_zone_lookup(spark, zone_lookup_path)

        pickup_lookup = zone_lookup.select(
            F.col("LocationID").alias("pickup_location_id"),
            F.col("Zone").alias("pickup_zone"),
            F.col("Borough").alias("pickup_borough"),
        )
        dropoff_lookup = zone_lookup.select(
            F.col("LocationID").alias("dropoff_location_id"),
            F.col("Zone").alias("dropoff_zone"),
            F.col("Borough").alias("dropoff_borough"),
        )

        cleaned = cleaned.join(pickup_lookup, on="pickup_location_id", how="left")
        cleaned = cleaned.join(dropoff_lookup, on="dropoff_location_id", how="left")
    except Exception:
        # If the zone lookup file is unavailable, fall back to raw IDs so
        # the rest of the pipeline can still run.
        cleaned = cleaned.withColumn(
            "pickup_zone", F.col("pickup_location_id").cast("string")
        )
        cleaned = cleaned.withColumn("pickup_borough", F.lit(None).cast("string"))
        cleaned = cleaned.withColumn(
            "dropoff_zone", F.col("dropoff_location_id").cast("string")
        )
        cleaned = cleaned.withColumn("dropoff_borough", F.lit(None).cast("string"))

    return cleaned
