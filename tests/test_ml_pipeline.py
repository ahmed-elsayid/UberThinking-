"""
test_ml_pipeline.py
---------------------
Purpose:
    Unit/integration tests for the ML pipeline (ml/pipeline.py,
    ml/train_model.py, ml/predict.py).

Suggested test cases:
    - test_pipeline_builds_without_error: build_pipeline() returns a valid
      unfit Pipeline object with the expected stages.
    - test_pipeline_fits_on_sample_data: pipeline.fit(...) succeeds on a
      small, synthetic DataFrame with the expected feature columns.
    - test_model_predicts_reasonable_range: predicted fares on synthetic
      inputs fall within a sane numeric range (e.g. > 0).
    - test_predict_fare_returns_float: ml/predict.py's predict_fare(...)
      returns a plain Python float, not a Spark Row/Column type.

Dependencies:
    - pytest
    - pyspark (a local SparkSession fixture, scope="module")
"""

# TODO: implement fixtures + test functions described above.
