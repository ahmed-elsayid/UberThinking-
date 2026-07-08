"""
config.py
---------
All settings and paths in one place, plus a helper to build a SparkSession.
Every other file imports from here so nothing is hardcoded.
"""

import os
import sys

from dotenv import load_dotenv

# Load values from a local .env file if one exists (optional).
load_dotenv()

# --- Folders and files ---
HISTORICAL_DATA_PATH = os.getenv("HISTORICAL_DATA_PATH", "data/raw")
ZONE_LOOKUP_PATH = os.getenv("ZONE_LOOKUP_PATH", "data/zone_lookup/taxi_zone_lookup.csv")
STREAM_INPUT_PATH = os.getenv("STREAM_INPUT_PATH", "data/stream")
RIDES_OUTPUT_PATH = os.getenv("RIDES_OUTPUT_PATH", "output/rides")
CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", "output/checkpoint")
MODEL_PATH = os.getenv("MODEL_PATH", "models/fare_model")

# How fast the fake live feed writes new files (seconds between batches).
STREAM_DELAY_SECONDS = float(os.getenv("STREAM_DELAY_SECONDS", "2"))
STREAM_BATCH_SIZE = int(os.getenv("STREAM_BATCH_SIZE", "50"))


def _apply_windows_fixes() -> None:
    """On Windows, PySpark needs a couple of environment hints to start.

    - PYSPARK_PYTHON: point Spark at this exact interpreter (not "python3").
    - HADOOP_HOME: folder holding bin/winutils.exe + bin/hadoop.dll.
      Set it in .env if Spark complains about "HADOOP_HOME ... unset".
    """
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

    hadoop_home = os.getenv("HADOOP_HOME", "")
    if hadoop_home:
        os.environ["HADOOP_HOME"] = hadoop_home
        hadoop_bin = os.path.join(hadoop_home, "bin")
        os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")

    # Spark 3.5 needs Java 11 or 17. Point it at the right JDK if JAVA_HOME
    # is set in .env, without touching the system-wide default.
    java_home = os.getenv("JAVA_HOME", "")
    if java_home:
        os.environ["JAVA_HOME"] = java_home
        java_bin = os.path.join(java_home, "bin")
        os.environ["PATH"] = java_bin + os.pathsep + os.environ.get("PATH", "")


def build_spark(app_name: str = "UberThinking"):
    """Creates a local SparkSession. Used by the streaming job and training."""
    _apply_windows_fixes()

    # Imported here so simple scripts (e.g. the stream generator) don't need
    # PySpark just to read the config values above.
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName(app_name).master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


# Apply the environment fixes as soon as config is imported, so ANY code that
# creates a SparkSession (including tests that build their own) inherits the
# correct PYSPARK_PYTHON / HADOOP_HOME / JAVA_HOME settings. Safe to run more
# than once.
_apply_windows_fixes()
