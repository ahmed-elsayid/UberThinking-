# Architecture & Design Notes

This document captures the reasoning behind TaxiPulse's structure, the
assumptions made when turning the original project brief into this
blueprint, and notes on how to extend it.

## 1. Data Flow

```text
NYC Taxi historical dataset (data/raw/)
        │
        ▼
Kafka Producer (producer/kafka_producer.py)
  - replays rows one at a time with a configurable delay
        │
        ▼
Kafka topic: taxi_rides
        │
        ▼
Spark Structured Streaming (streaming/spark_stream_consumer.py)
  - parses JSON with an explicit schema (streaming/schema.py)
  - cleans + engineers features (preprocessing/cleaning.py)
  - computes aggregations (analytics/analytics.py)
        │
        ├──▶ output/parquet/rides/        (cleaned ride-level records)
        └──▶ output/parquet/aggregates/   (windowed metrics)
                        │
                        ▼
        ml/train_model.py (batch, run separately/offline)
          - trains + evaluates a Random Forest fare-prediction model
          - saves to models/fare_prediction
                        │
                        ▼
        Streamlit Dashboard (dashboard/)
          - Overview, Location Analytics, Ride Explorer, Prediction,
            Streaming Monitor pages
          - reads output/parquet/ for analytics pages
          - calls ml/predict.py (loading models/fare_prediction) for the
            Prediction page
```

## 2. Requirements Review — Gaps Identified in the Original Brief

The original project description is strong and detailed, but a few points
needed clarification or a concrete decision to be buildable:

| Area | Gap in original brief | Resolution in this blueprint |
|------|------------------------|-------------------------------|
| Dataset source | "NYC Taxi Dataset" named but no specific file/version | Assumed NYC TLC Yellow Taxi Trip Records (monthly Parquet/CSV); documented in `data/raw/README.md`. Team should pick one specific month for consistency. |
| Location fields | Spec lists "pickup_location"/"dropoff_location" as if they were names | TLC data actually encodes these as integer `LocationID`s; a zone lookup file is required to get names. Added `data/zone_lookup/`. |
| Storage format | Spec says "Parquet (or Delta Lake if allowed)" | Defaulted to Parquet only, to keep scope beginner-friendly; Delta Lake noted here as a future upgrade (adds ACID transactions + upserts, useful if the team later needs to handle late-arriving/duplicate events more robustly). |
| Config management | Spec's file tree has no config/env layer | Added `config/config.py` + `.env.example` so Kafka addresses, paths, and timing constants aren't hardcoded across multiple files — this is the single biggest maintainability improvement over the original structure. |
| Testing | Not mentioned in the original spec | Added `tests/` with pytest placeholders for cleaning, analytics, and ML pipeline — important for a Spark project, since bugs in transformation logic are easy to introduce and hard to spot visually. |
| Streaming Monitor page | Spec implies true real-time updates | Streamlit has no native push-based real-time updates; documented the realistic approach (polling/manual refresh) directly in `dashboard/pages/5_streaming_monitor.py` rather than overpromising true real-time behavior. |
| Docker | Marked optional with no detail | Kept optional, but gave it a concrete purpose (local Kafka/Zookeeper) and a fallback (point at any existing broker) so teams without Docker experience aren't blocked. |
| Team size | Fixed at "4 Members" | Kept the 4-role split as the default suggestion but noted in the README that it should be adapted to whatever team size the group actually has. |

## 3. Possible Future Improvements

- Swap Parquet for Delta Lake if the team wants upserts/schema evolution.
- Add a `notebooks/` folder for exploratory data analysis, kept separate
  from production code paths.
- Add CI (GitHub Actions) to run `pytest` automatically on push.
- Add a `Makefile` or `justfile` to standardize common commands (start
  Kafka, run producer, run consumer, train model, launch dashboard) once
  the exact commands are finalized.
- Containerize the whole pipeline (producer, consumer, dashboard) as
  separate Docker services for a fully reproducible one-command demo.
