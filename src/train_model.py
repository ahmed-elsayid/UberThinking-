"""
train_model.py
--------------
Trains the fare-prediction model ONCE on the historical NYC taxi dataset
using Spark MLlib, prints its accuracy, and saves it to models/. Run this a
single time before using the dashboard's Prediction page.

Run:
    python src/train_model.py
"""

from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor

from config import HISTORICAL_DATA_PATH, MODEL_PATH, build_spark
from transforms import clean_and_engineer

# Columns fed to the model.
CATEGORICAL = ["pickup_zone", "dropoff_zone"]
NUMERIC = ["trip_distance", "pickup_hour", "passenger_count", "ride_duration_minutes"]
LABEL = "fare_amount"

# The full NYC monthly file has millions of rows, which is slow and memory-
# heavy to train on locally. A sample this size is plenty for a good demo
# model and trains in well under a minute.
TRAINING_SAMPLE_SIZE = 200_000


def load_historical(spark):
    """Reads the raw historical dataset and renames TLC columns to our names.

    `pathGlobFilter` keeps Spark to only the .parquet files, so other files in
    data/raw/ (like README.md) are ignored instead of failing the read.
    """
    df = spark.read.option("pathGlobFilter", "*.parquet").parquet(HISTORICAL_DATA_PATH)
    renames = {
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime",
        "PULocationID": "pickup_location_id",
        "DOLocationID": "dropoff_location_id",
    }
    for old, new in renames.items():
        if old in df.columns:
            df = df.withColumnRenamed(old, new)
    return df


def build_pipeline() -> Pipeline:
    """Index the zone names, combine all features, then a Random Forest."""
    indexers = [
        StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep")
        for c in CATEGORICAL
    ]
    assembler = VectorAssembler(
        inputCols=NUMERIC + [f"{c}_idx" for c in CATEGORICAL],
        outputCol="features",
        handleInvalid="skip",
    )
    forest = RandomForestRegressor(
        featuresCol="features",
        labelCol=LABEL,
        predictionCol="predicted_fare",
        numTrees=50,
        maxDepth=8,
        # The zone columns are categorical with ~260 values (NYC has 265 taxi
        # zones), so maxBins must be at least that large.
        maxBins=300,
        seed=42,
    )
    return Pipeline(stages=indexers + [assembler, forest])


def main() -> None:
    spark = build_spark("UberThinking-Training")

    data = clean_and_engineer(load_historical(spark), spark)

    # Train on a sample so this runs fast on a laptop instead of thrashing
    # through millions of rows.
    total_rows = data.count()
    if total_rows > TRAINING_SAMPLE_SIZE:
        data = data.sample(fraction=TRAINING_SAMPLE_SIZE / total_rows, seed=42)
    data = data.cache()
    print(f"Training on ~{TRAINING_SAMPLE_SIZE:,} of {total_rows:,} rides.")

    # A quick Spark SQL peek at the data before training.
    data.createOrReplaceTempView("rides")
    print("Average fare by pickup hour (top 5):")
    spark.sql(
        "SELECT pickup_hour, ROUND(AVG(fare_amount), 2) AS avg_fare "
        "FROM rides GROUP BY pickup_hour ORDER BY avg_fare DESC LIMIT 5"
    ).show()

    train_df, test_df = data.randomSplit([0.8, 0.2], seed=42)

    model = build_pipeline().fit(train_df)
    predictions = model.transform(test_df)

    rmse = RegressionEvaluator(
        labelCol=LABEL, predictionCol="predicted_fare", metricName="rmse"
    ).evaluate(predictions)
    print(f"\nModel trained. Test RMSE: {rmse:.2f}")

    model.write().overwrite().save(MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
