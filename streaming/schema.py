"""
schema.py
---------
Explicit Spark StructType schema for incoming Kafka JSON messages.
Structured Streaming requires an explicit schema when parsing JSON from a
streaming source (it cannot infer schema like it can for static files).
"""

from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# Field order/names must align exactly with the JSON keys produced by
# producer/kafka_producer.py.
RIDE_SCHEMA = StructType(
    [
        StructField("pickup_datetime", StringType(), True),
        StructField("dropoff_datetime", StringType(), True),
        StructField("trip_distance", DoubleType(), True),
        StructField("pickup_location_id", IntegerType(), True),
        StructField("dropoff_location_id", IntegerType(), True),
        StructField("fare_amount", DoubleType(), True),
        StructField("tip_amount", DoubleType(), True),
        StructField("passenger_count", IntegerType(), True),
        StructField("payment_type", StringType(), True),
    ]
)
