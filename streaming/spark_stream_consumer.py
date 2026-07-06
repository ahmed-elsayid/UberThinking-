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
