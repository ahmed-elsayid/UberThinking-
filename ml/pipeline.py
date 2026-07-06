"""
pipeline.py
-----------
Purpose:
    Defines the reusable Spark ML Pipeline (feature transformation stages
    + estimator) used for fare prediction. Kept separate from
    train_model.py so the exact same pipeline definition can be reused for
    training, evaluation, and (if needed) re-training later.

Responsibilities:
    - Define categorical encoding stages:
        - StringIndexer for pickup_zone, dropoff_zone, payment_type
        - OneHotEncoder on the indexed columns
    - Define VectorAssembler combining numeric + encoded categorical
      features into a single "features" column:
        - trip_distance, pickup_hour, passenger_count,
          ride_duration_minutes, encoded pickup_zone, encoded dropoff_zone
    - Define the regression estimator:
        - RandomForestRegressor (default choice — handles nonlinearity,
          minimal feature scaling needed)
        - Document GBTRegressor / LinearRegression as alternatives to try
    - Assemble all stages into a single Pipeline object.

Expected input:
    - Cleaned, feature-engineered Spark DataFrame (see preprocessing/cleaning.py)
      with target column fare_amount.

Expected output:
    - An unfit pyspark.ml.Pipeline object, ready to `.fit(training_df)`.

Dependencies:
    - pyspark.ml.feature (StringIndexer, OneHotEncoder, VectorAssembler)
    - pyspark.ml.regression (RandomForestRegressor, GBTRegressor,
      LinearRegression)
    - pyspark.ml.Pipeline

Consumed by:
    - ml/train_model.py
"""

# TODO: def build_pipeline(): ... return Pipeline(stages=[...])
