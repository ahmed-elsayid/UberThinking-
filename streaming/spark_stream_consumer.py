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
        # Don't crash if checkpointed offsets are no longer in Kafka — e.g.
        # after the broker/topic is recreated (docker compose down/up) while
        # an old checkpoint still references purged offsets. Skip the gap and
        # resume instead of aborting the query.
        .option("failOnDataLoss", "false")
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
