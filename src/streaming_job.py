"""
streaming_job.py
----------------
Spark Structured Streaming using the FILE source (no Kafka). It watches the
data/stream/ folder and streams any new CSV or Parquet files dropped there:
it cleans each micro-batch and appends the results as Parquet to
output/rides/, which the dashboard reads.

- Drop a .csv or .parquet file into data/stream/ and it gets streamed.
- Starting with an empty folder is fine — the job just waits for files.

Run:
    python src/streaming_job.py
"""

import os

from config import CHECKPOINT_PATH, RIDES_OUTPUT_PATH, STREAM_INPUT_PATH, build_spark
from transforms import RIDE_SCHEMA, clean_and_engineer


def _append_batch(batch_df, _batch_id) -> None:
    """Appends one cleaned micro-batch to the rides Parquet folder.

    We append with a plain batch write (instead of the streaming Parquet
    sink) so the CSV and Parquet queries can safely share one output folder —
    the streaming sink keeps a private metadata dir that two queries can't
    share.
    """
    if not batch_df.isEmpty():
        batch_df.write.mode("append").parquet(RIDES_OUTPUT_PATH)


def start_stream(spark, file_format: str, glob_pattern: str):
    """Starts one streaming query that watches STREAM_INPUT_PATH for files of
    a single format (csv or parquet) and appends cleaned rides to Parquet.

    Providing RIDE_SCHEMA explicitly means Spark never has to infer a schema,
    so an empty folder doesn't crash the query — it simply waits for files.
    Each format gets its own checkpoint so the two queries don't clash.
    """
    reader = (
        spark.readStream.schema(RIDE_SCHEMA)
        .option("maxFilesPerTrigger", 1)  # one file per micro-batch = visibly "live"
        .option("pathGlobFilter", glob_pattern)  # only this format's files
    )
    if file_format == "csv":
        reader = reader.option("header", True)

    raw = reader.format(file_format).load(STREAM_INPUT_PATH)
    cleaned = clean_and_engineer(raw, spark)

    return (
        cleaned.writeStream.foreachBatch(_append_batch)
        .option("checkpointLocation", os.path.join(CHECKPOINT_PATH, file_format))
        .outputMode("append")
        .start()
    )


def main() -> None:
    spark = build_spark("UberThinking-Streaming")

    # Make sure the watched folder exists so an empty start doesn't error.
    os.makedirs(STREAM_INPUT_PATH, exist_ok=True)

    # Watch for both CSV and Parquet files in the same folder.
    start_stream(spark, "csv", "*.csv")
    start_stream(spark, "parquet", "*.parquet")

    print(f"Watching {STREAM_INPUT_PATH}/ for new .csv / .parquet files.")
    print(f"Writing cleaned rides to {RIDES_OUTPUT_PATH}/  (Ctrl+C to stop)")
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
