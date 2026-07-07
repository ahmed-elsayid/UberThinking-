"""
schema.py
---------
Purpose:
    Defines the explicit Spark StructType schema for incoming Kafka JSON
    messages. Structured Streaming requires an explicit schema when parsing
    JSON from Kafka (it cannot infer schema from a streaming source).

Responsibilities:
    - Define one StructType constant, e.g. RIDE_SCHEMA, listing every field
      produced by producer/kafka_producer.py with the correct Spark type.

Expected fields (align exactly with the producer's JSON keys):
    - pickup_datetime       StringType (parsed to TimestampType downstream)
    - dropoff_datetime      StringType (parsed to TimestampType downstream)
    - trip_distance         DoubleType
    - pickup_location_id    IntegerType
    - dropoff_location_id   IntegerType
    - fare_amount           DoubleType
    - tip_amount            DoubleType
    - passenger_count       IntegerType
    - payment_type          StringType

Dependencies:
    - pyspark.sql.types (StructType, StructField, StringType, DoubleType,
      IntegerType)

Consumed by:
    - streaming/spark_stream_consumer.py (from_json(col("value"), RIDE_SCHEMA))
"""

# TODO: define RIDE_SCHEMA = StructType([...])


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
