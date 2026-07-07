"""
spark_stream_consumer.py
-------------------------
Purpose:
    Entry point for the real-time pipeline. Reads from the Kafka topic
    using Spark Structured Streaming, parses JSON into a DataFrame,
    applies cleaning/feature engineering, computes streaming analytics,
    and writes results to two sinks: aggregated metrics (for the
    dashboard's "live" views) and raw cleaned rides as Parquet (for
    historical analytics + ML training).

Responsibilities:
    - Create/get a SparkSession (name + master from config/config.py).
    - Read a streaming DataFrame from Kafka
      (format="kafka", subscribe=KAFKA_TOPIC).
    - Parse the Kafka `value` column as JSON using streaming/schema.py.
    - Call preprocessing/cleaning.py to clean + engineer features.
    - Call analytics/analytics.py to compute streaming aggregations.
    - Write:
        a) cleaned ride-level data -> Parquet sink (output/parquet/),
           with checkpointing (CHECKPOINT_PATH).
        b) aggregated metrics -> a sink the dashboard can read (e.g. a
           separate Parquet path, or an in-memory/foreachBatch sink that
           updates a lightweight store the dashboard polls).
    - Start the streaming query and await termination.

Expected input:
    - Kafka topic KAFKA_TOPIC (JSON messages matching streaming/schema.py).

Expected output:
    - output/parquet/rides/         (cleaned, ride-level Parquet)
    - output/parquet/aggregates/    (windowed/aggregated Parquet, or other
                                      sink used by the dashboard)

Dependencies:
    - pyspark (SparkSession, functions: from_json, col, window, etc.)
    - config/config.py
    - streaming/schema.py
    - preprocessing/cleaning.py
    - analytics/analytics.py

Run:
    spark-submit streaming/spark_stream_consumer.py
"""

# TODO:
#   1. spark = SparkSession.builder...getOrCreate()
#   2. raw_stream = spark.readStream.format("kafka")...load()
#   3. parsed = raw_stream.select(from_json(col("value").cast("string"), RIDE_SCHEMA).alias("data")).select("data.*")
#   4. cleaned = clean_and_engineer(parsed)          # preprocessing/cleaning.py
#   5. aggregates = compute_aggregations(cleaned)    # analytics/analytics.py
#   6. write cleaned -> parquet sink (with checkpoint)
#   7. write aggregates -> parquet/other sink (with checkpoint)
#   8. query.awaitTermination()


"""
spark_stream_consumer.py
-------------------------
Entry point for the real-time pipeline. Reads from the Kafka topic using
Spark Structured Streaming, parses JSON into a DataFrame, applies
cleaning/feature engineering, computes streaming analytics, and writes
results to two sinks:
    - output/parquet/rides/       cleaned, ride-level records (append)
    - output/parquet/aggregates/  per-metric aggregate snapshots, refreshed
                                   on every micro-batch via foreachBatch
                                   (windowed/grouped aggregations can't be
                                   written directly to a Parquet sink in
                                   append mode, so foreachBatch overwrites
                                   each metric's directory per batch).

Run:
    spark-submit streaming/spark_stream_consumer.py
"""

import os

# Load config (and .env) FIRST so HADOOP_HOME is in os.environ before PySpark starts
from config.config import (
    AGGREGATES_OUTPUT_PATH,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    RIDES_CHECKPOINT_PATH,
    RIDES_OUTPUT_PATH,
    SPARK_APP_NAME,
    SPARK_MASTER,
)

# On Windows, PySpark requires hadoop.dll to be in the PATH.
if os.name == "nt" and "HADOOP_HOME" in os.environ:
    hadoop_bin = os.path.join(os.environ["HADOOP_HOME"], "bin")
    os.environ["PATH"] += os.pathsep + hadoop_bin

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from analytics.analytics import compute_aggregations
from preprocessing.cleaning import clean_and_engineer
from streaming.schema import RIDE_SCHEMA


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName(SPARK_APP_NAME)
        .master(SPARK_MASTER)
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",
        )
        .getOrCreate()
    )


def read_kafka_stream(spark: SparkSession) -> DataFrame:
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )


def parse_ride_events(raw_stream: DataFrame) -> DataFrame:
    return raw_stream.select(
        F.from_json(F.col("value").cast("string"), RIDE_SCHEMA).alias("data")
    ).select("data.*")


def write_aggregates_batch(batch_df: DataFrame, batch_id: int) -> None:
    """foreachBatch sink: computes every aggregation on this micro-batch and
    overwrites each metric's Parquet directory so dashboard reads always
    see the latest snapshot.
    """
    if batch_df.rdd.isEmpty():
        return

    aggregates = compute_aggregations(batch_df)
    for metric_name, metric_df in aggregates.items():
        out_path = os.path.join(AGGREGATES_OUTPUT_PATH, metric_name)
        metric_df.write.mode("overwrite").parquet(out_path)


def run() -> None:
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    raw_stream = read_kafka_stream(spark)
    parsed = parse_ride_events(raw_stream)
    cleaned = clean_and_engineer(parsed, spark=spark)

    # Sink A: cleaned ride-level rows -> Parquet (append), for the Ride
    # Explorer page and offline ML training.
    rides_query = (
        cleaned.writeStream.format("parquet")
        .option("path", RIDES_OUTPUT_PATH)
        .option("checkpointLocation", RIDES_CHECKPOINT_PATH)
        .outputMode("append")
        .start()
    )

    # Sink B: aggregated metrics -> refreshed Parquet snapshots via
    # foreachBatch, for the Overview / Streaming Monitor pages.
    aggregates_query = (
        cleaned.writeStream.foreachBatch(write_aggregates_batch)
        .outputMode("update")
        .start()
    )

    rides_query.awaitTermination()
    aggregates_query.awaitTermination()


if __name__ == "__main__":
    run()
