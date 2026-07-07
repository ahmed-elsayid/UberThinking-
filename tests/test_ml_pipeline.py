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


"""
test_ml_pipeline.py
---------------------
Unit/integration tests for the ML pipeline (ml/pipeline.py,
ml/train_model.py, ml/predict.py).
"""

import pytest
from pyspark.ml import Pipeline, PipelineModel
from pyspark.sql import Row, SparkSession

from ml.pipeline import build_pipeline


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.appName("test_ml_pipeline")
        .master("local[1]")
        .getOrCreate()
    )
    yield session
    session.stop()


@pytest.fixture(scope="module")
def sample_training_df(spark):
    rows = [
        Row(
            trip_distance=2.0,
            pickup_hour=8,
            passenger_count=1,
            ride_duration_minutes=10.0,
            pickup_zone="Zone A",
            dropoff_zone="Zone B",
            payment_type="Card",
            fare_amount=10.0,
        ),
        Row(
            trip_distance=5.0,
            pickup_hour=17,
            passenger_count=2,
            ride_duration_minutes=20.0,
            pickup_zone="Zone B",
            dropoff_zone="Zone C",
            payment_type="Cash",
            fare_amount=22.0,
        ),
        Row(
            trip_distance=1.0,
            pickup_hour=12,
            passenger_count=1,
            ride_duration_minutes=6.0,
            pickup_zone="Zone A",
            dropoff_zone="Zone C",
            payment_type="Card",
            fare_amount=7.5,
        ),
        Row(
            trip_distance=8.0,
            pickup_hour=22,
            passenger_count=3,
            ride_duration_minutes=30.0,
            pickup_zone="Zone C",
            dropoff_zone="Zone A",
            payment_type="Cash",
            fare_amount=33.0,
        ),
    ]
    return spark.createDataFrame(rows)


def test_pipeline_builds_without_error():
    pipeline = build_pipeline()
    assert isinstance(pipeline, Pipeline)
    assert len(pipeline.getStages()) > 0


def test_pipeline_fits_on_sample_data(sample_training_df):
    pipeline = build_pipeline()
    model = pipeline.fit(sample_training_df)
    assert isinstance(model, PipelineModel)


def test_model_predicts_reasonable_range(sample_training_df):
    pipeline = build_pipeline()
    model = pipeline.fit(sample_training_df)
    predictions = model.transform(sample_training_df)
    values = [r["predicted_fare"] for r in predictions.select("predicted_fare").collect()]
    assert all(v > 0 for v in values)


def test_predict_fare_returns_float(sample_training_df, tmp_path, monkeypatch):
    pipeline = build_pipeline()
    model = pipeline.fit(sample_training_df)
    model_path = str(tmp_path / "fare_prediction")
    model.write().overwrite().save(model_path)

    import ml.predict as predict_module

    monkeypatch.setattr(predict_module, "MODEL_PATH", model_path)
    predict_module._get_model.cache_clear()
    predict_module._get_spark.cache_clear()

    fare = predict_module.predict_fare(
        distance=3.0,
        passengers=1,
        pickup_hour=9,
        pickup_zone="Zone A",
        dropoff_zone="Zone B",
    )
    assert isinstance(fare, float)
