"""
train_model.py
--------------
Purpose:
    Trains the fare-prediction model on historical/cleaned data, evaluates
    it, and persists the trained pipeline model to disk for the dashboard's
    prediction page to load.

Responsibilities:
    - Load cleaned historical data (batch read of output/parquet/rides/,
      or a static batch read of data/raw/ passed through
      preprocessing/cleaning.py).
    - Split into train/test sets (e.g. 80/20).
    - Build the pipeline via ml/pipeline.py.
    - Fit the pipeline on the training set.
    - Evaluate on the test set using RegressionEvaluator:
        - RMSE (Root Mean Squared Error)
        - MAE (Mean Absolute Error)
    - Log/print evaluation metrics for the team's report.
    - Save the fitted PipelineModel to MODEL_PATH
      (e.g. "models/fare_prediction").

Expected input:
    - Cleaned Spark DataFrame with fare_amount as target and the feature
      columns listed in ml/pipeline.py.

Expected output:
    - Trained model artifacts written to MODEL_PATH.
    - Printed/logged RMSE and MAE.

Dependencies:
    - pyspark.ml.evaluation (RegressionEvaluator)
    - ml/pipeline.py
    - preprocessing/cleaning.py
    - config/config.py

Run:
    spark-submit ml/train_model.py
"""

# TODO:
#   1. Load + clean historical data.
#   2. train_df, test_df = df.randomSplit([0.8, 0.2])
#   3. pipeline = build_pipeline()
#   4. model = pipeline.fit(train_df)
#   5. predictions = model.transform(test_df)
#   6. evaluate with RegressionEvaluator (rmse, mae)
#   7. model.write().overwrite().save(MODEL_PATH)


"""
train_model.py
--------------
Trains the fare-prediction model on historical/cleaned data, evaluates it,
and persists the trained pipeline model to disk for the dashboard's
prediction page to load.

Run:
    spark-submit ml/train_model.py
"""

import logging
import os

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql import SparkSession

from config.config import MODEL_PATH, RAW_DATA_PATH, RIDES_OUTPUT_PATH, SPARK_APP_NAME, SPARK_MASTER
from ml.pipeline import LABEL_COLUMN, build_pipeline
from preprocessing.cleaning import clean_and_engineer
from streaming.schema import RIDE_SCHEMA

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def build_spark_session() -> SparkSession:
    return SparkSession.builder.appName(SPARK_APP_NAME).master(SPARK_MASTER).getOrCreate()


def load_training_data(spark: SparkSession):
    """Prefers already-cleaned streaming output (output/parquet/rides/);
    falls back to a static batch read + clean of the raw dataset.
    """
    if os.path.exists(RIDES_OUTPUT_PATH) and os.listdir(RIDES_OUTPUT_PATH):
        logger.info("Loading cleaned data from %s", RIDES_OUTPUT_PATH)
        return spark.read.parquet(RIDES_OUTPUT_PATH)

    logger.info("Falling back to raw data at %s", RAW_DATA_PATH)
    if RAW_DATA_PATH.endswith(".parquet"):
        raw_df = spark.read.parquet(RAW_DATA_PATH)
    else:
        raw_df = spark.read.option("header", True).schema(RIDE_SCHEMA).csv(RAW_DATA_PATH)

    return clean_and_engineer(raw_df, spark=spark)


def run() -> None:
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    df = load_training_data(spark)

    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

    pipeline = build_pipeline()
    model = pipeline.fit(train_df)

    predictions = model.transform(test_df)

    evaluator_rmse = RegressionEvaluator(
        labelCol=LABEL_COLUMN, predictionCol="predicted_fare", metricName="rmse"
    )
    evaluator_mae = RegressionEvaluator(
        labelCol=LABEL_COLUMN, predictionCol="predicted_fare", metricName="mae"
    )

    rmse = evaluator_rmse.evaluate(predictions)
    mae = evaluator_mae.evaluate(predictions)

    logger.info("Evaluation results -- RMSE: %.4f, MAE: %.4f", rmse, mae)
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE:  {mae:.4f}")

    model.write().overwrite().save(MODEL_PATH)
    logger.info("Model saved to %s", MODEL_PATH)


if __name__ == "__main__":
    run()
