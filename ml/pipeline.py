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


"""
pipeline.py
-----------
Defines the reusable Spark ML Pipeline (feature transformation stages +
estimator) used for fare prediction. Kept separate from train_model.py so
the exact same pipeline definition can be reused for training, evaluation,
and re-training later.

Alternatives to RandomForestRegressor (swap the `estimator` stage if you
want to experiment):
    - GBTRegressor: often higher accuracy, slower to train, more prone to
      overfitting on small datasets.
    - LinearRegression: fastest, most interpretable, but assumes linear
      relationships and needs feature scaling to perform well.
"""

from pyspark.ml import Pipeline
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor

CATEGORICAL_COLUMNS = ["pickup_zone", "dropoff_zone", "payment_type"]
NUMERIC_COLUMNS = [
    "trip_distance",
    "pickup_hour",
    "passenger_count",
    "ride_duration_minutes",
]
LABEL_COLUMN = "fare_amount"
FEATURES_COLUMN = "features"


def build_pipeline() -> Pipeline:
    """Builds an unfit Spark ML Pipeline for fare prediction.

    Stages:
        1. StringIndexer for each categorical column.
        2. OneHotEncoder on the indexed categorical columns.
        3. VectorAssembler combining numeric + one-hot encoded columns.
        4. RandomForestRegressor predicting `fare_amount`.
    """
    indexers = [
        StringIndexer(
            inputCol=col_name,
            outputCol=f"{col_name}_index",
            handleInvalid="keep",
        )
        for col_name in CATEGORICAL_COLUMNS
    ]

    encoder = OneHotEncoder(
        inputCols=[f"{col_name}_index" for col_name in CATEGORICAL_COLUMNS],
        outputCols=[f"{col_name}_ohe" for col_name in CATEGORICAL_COLUMNS],
    )

    assembler = VectorAssembler(
        inputCols=NUMERIC_COLUMNS + [f"{col_name}_ohe" for col_name in CATEGORICAL_COLUMNS],
        outputCol=FEATURES_COLUMN,
        handleInvalid="skip",
    )

    regressor = RandomForestRegressor(
        featuresCol=FEATURES_COLUMN,
        labelCol=LABEL_COLUMN,
        predictionCol="predicted_fare",
        numTrees=100,
        maxDepth=10,
        seed=42,
    )

    return Pipeline(stages=indexers + [encoder, assembler, regressor])
