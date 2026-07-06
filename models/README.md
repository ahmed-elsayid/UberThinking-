# models/

Purpose:
    Destination for trained Spark ML PipelineModel artifacts (produced by
    ml/train_model.py, consumed by ml/predict.py). This folder is
    gitignored — trained models are regenerated from code + data, not
    committed to version control.

Expected contents (after training):
    - fare_prediction/   (a Spark ML model directory — contains its own
                           metadata + data subfolders; do not rename or
                           reorganize the internal Spark-generated structure)

Note:
    If model files must be shared with teammates outside of git, use a
    shared drive, cloud storage bucket, or a release artifact — not the
    repository.
