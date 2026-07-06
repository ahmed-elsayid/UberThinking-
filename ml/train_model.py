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
