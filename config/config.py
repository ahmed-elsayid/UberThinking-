"""
config.py
---------
Single source of truth for all environment-dependent settings (Kafka
connection info, file paths, Spark app name, producer timing, etc.).
Every other module imports from here instead of hardcoding values or
reading os.environ directly.
"""

import os
import sys

from dotenv import load_dotenv

# Load variables from a .env file in the project root (if present).
# Falls back to already-exported environment variables / defaults below.
load_dotenv()


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# --- PySpark driver Python + Windows/Hadoop fixes ---
# Must happen before any SparkSession is created (every entry point imports
# this module first, so this is the right place). Without these, PySpark on
# Windows fails during SparkContext init with errors like "Missing Python
# executable 'python3'" or "HADOOP_HOME and hadoop.home.dir are unset" —
# these look unrelated to Kafka but happen before Spark ever reaches Kafka.

# Make PySpark use the current interpreter (the venv's python.exe) instead
# of guessing "python3", which doesn't exist by that name on Windows.
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

# On Windows, Spark's bundled Hadoop libraries need winutils.exe + hadoop.dll
# available via HADOOP_HOME. Set HADOOP_HOME=C:\hadoop (or wherever you
# extracted winutils) in your .env to fix "HADOOP_HOME and hadoop.home.dir
# are unset" errors. See README.md's Windows setup notes.
HADOOP_HOME: str = os.getenv("HADOOP_HOME", "")
if HADOOP_HOME:
    os.environ.setdefault("HADOOP_HOME", HADOOP_HOME)
    hadoop_bin = os.path.join(HADOOP_HOME, "bin")
    if hadoop_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = hadoop_bin + os.pathsep + os.environ.get("PATH", "")

# Spark 3.5 requires Java 11/17 and does not support Java 8. If a machine's
# default `java` is Java 8, set JAVA_HOME=<path to JDK 17> in .env; this points
# Spark at it (and puts its bin first on PATH) before any SparkSession starts,
# without changing the system-wide default.
JAVA_HOME: str = os.getenv("JAVA_HOME", "")
if JAVA_HOME:
    os.environ["JAVA_HOME"] = JAVA_HOME
    java_bin = os.path.join(JAVA_HOME, "bin")
    if java_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = java_bin + os.pathsep + os.environ.get("PATH", "")

# --- Kafka ---
KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "taxi_rides")

# --- Spark ---
SPARK_MASTER: str = os.getenv("SPARK_MASTER", "local[*]")
SPARK_APP_NAME: str = os.getenv("SPARK_APP_NAME", "UberThinking")

# --- File paths ---
RAW_DATA_PATH: str = os.getenv("RAW_DATA_PATH", "data/raw")
ZONE_LOOKUP_PATH: str = os.getenv("ZONE_LOOKUP_PATH", "data/zone_lookup/taxi_zone_lookup.csv")
CHECKPOINT_PATH: str = os.getenv("CHECKPOINT_PATH", "output/checkpoints/")
PARQUET_OUTPUT_PATH: str = os.getenv("PARQUET_OUTPUT_PATH", "output/parquet/")
MODEL_PATH: str = os.getenv("MODEL_PATH", "models/fare_prediction")

# Derived, commonly used sub-paths under PARQUET_OUTPUT_PATH.
RIDES_OUTPUT_PATH: str = os.path.join(PARQUET_OUTPUT_PATH, "rides")
AGGREGATES_OUTPUT_PATH: str = os.path.join(PARQUET_OUTPUT_PATH, "aggregates")
RIDES_CHECKPOINT_PATH: str = os.path.join(CHECKPOINT_PATH, "rides")
AGGREGATES_CHECKPOINT_PATH: str = os.path.join(CHECKPOINT_PATH, "aggregates")

# --- Producer behavior ---
PRODUCER_DELAY_SECONDS: float = _get_float("PRODUCER_DELAY_SECONDS", 0.5)
