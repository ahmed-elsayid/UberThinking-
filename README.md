# 🚕 UberThinking — Real-Time Ride Intelligence using Apache Spark

UberThinking is a real-time analytics and fare-prediction platform built on the
Apache Spark ecosystem. It simulates a live taxi-dispatch data feed (in the
style of Uber/Careem), processes it through Kafka and Spark Structured
Streaming, stores curated results as Parquet, trains a fare-prediction model
with Spark MLlib, and surfaces everything in an interactive Streamlit
dashboard.

Every file in this repository is fully implemented and ready to run end to
end — from the Kafka producer through Structured Streaming, ML training, and
the Streamlit dashboard.

---

## 1. Business Problem

A ride-hailing operator needs to answer, in near real time:

- Where is rider demand increasing right now?
- Which pickup/dropoff zones are busiest?
- What is current revenue and average fare?
- How long are rides taking?
- Can we estimate a fare *before* the ride starts?

UberThinking continuously ingests ride events, processes and aggregates them,
trains a predictive model offline, and visualizes both live and historical
insight in one dashboard.

## 2. Architecture

```text
                    NYC Taxi Dataset (historical, replayed as a live feed)
                           │
                           ▼
                   Kafka Producer  (producer/kafka_producer.py)
                           │
                           ▼
                  Kafka Topic: taxi_rides
                           │
                           ▼
         Spark Structured Streaming Consumer (streaming/)
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
  Streaming Analytics (analytics/)   Cleaned Feature Storage
          │                                 │
          ▼                                 ▼
    Aggregated Metrics                 Parquet (output/parquet)
          │                                 │
          └──────────────┬──────────────────┘
                         ▼
             Spark ML Fare Prediction (ml/)
                         │
                         ▼
              Streamlit Dashboard (dashboard/)
```

## 3. Tech Stack

| Layer            | Technology                          |
|-------------------|--------------------------------------|
| Language          | Python 3.10+                        |
| Big Data Engine   | Apache Spark (PySpark)               |
| Streaming         | Spark Structured Streaming           |
| Messaging         | Apache Kafka                         |
| Machine Learning  | Spark MLlib                          |
| Storage           | Parquet                              |
| Dashboard         | Streamlit + Plotly                   |
| Config            | python-dotenv                        |
| Orchestration     | Docker Compose (optional, local dev) |
| Testing           | pytest                               |
| Data Source       | NYC TLC Yellow Taxi Trip Records     |

## 4. Project Structure

```text
UberThinking/
├── README.md                  Project overview (this file)
├── LICENSE                    Open-source license
├── .gitignore                 Files/folders excluded from git
├── requirements.txt           Python dependencies
├── .env.example                Sample environment configuration
├── docker/                    Local Kafka + Spark dev environment
│   ├── docker-compose.yml
│   └── README.md
├── config/                    Centralized app configuration
│   └── config.py
├── data/
│   ├── raw/                   Downloaded NYC Taxi source data (gitignored)
│   └── zone_lookup/           Taxi zone ID -> borough/zone name lookup
├── producer/                  Kafka producer that replays historical rides
│   └── kafka_producer.py
├── streaming/                 Spark Structured Streaming consumer
│   ├── schema.py
│   └── spark_stream_consumer.py
├── preprocessing/             Data cleaning & feature engineering
│   └── cleaning.py
├── analytics/                 Streaming SQL aggregations
│   └── analytics.py
├── ml/                        Spark MLlib fare-prediction pipeline
│   ├── pipeline.py
│   ├── train_model.py
│   └── predict.py
├── dashboard/                 Streamlit multipage app
│   ├── app.py
│   └── pages/
│       ├── 1_overview.py
│       ├── 2_location_analytics.py
│       ├── 3_ride_explorer.py
│       ├── 4_prediction.py
│       └── 5_streaming_monitor.py
├── models/                    Saved/trained ML models (gitignored)
├── output/
│   └── parquet/               Streaming sink output (gitignored)
├── tests/                     Unit tests
│   ├── test_cleaning.py
│   ├── test_analytics.py
│   └── test_ml_pipeline.py
├── scripts/                   One-off setup/dev scripts
│   └── setup_kafka_topic.md
└── docs/
    └── architecture.md        Deeper design notes & decisions
```

## 5. How to Use

### 5.1 Prerequisites

- Python 3.10 or 3.11
- Java 11 (required by PySpark)
- Docker + Docker Compose (optional — only needed if you don't already
  have a Kafka broker to point at)

### 5.2 Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/ahmed-elsayid/UberThinking- && cd UberThinking-

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies (pinned in pyproject.toml)
pip install -e ".[test]"

# 4. Copy environment config and adjust if needed
cp .env.example .env
```

### 5.3 Get the data

1. Download one month of NYC TLC "Yellow Taxi Trip Records" (Parquet or
   CSV) from the official TLC Trip Record Data page and place it under
   `data/raw/` (see `data/raw/README.md`). Point `RAW_DATA_PATH` in `.env`
   at the file if the name differs from the default.
2. Download `taxi_zone_lookup.csv` (also published by TLC) into
   `data/zone_lookup/` (see `data/zone_lookup/README.md`).

### 5.4 Start Kafka

Use the bundled Docker Compose setup, or point at any Kafka broker you
already have:

```bash
docker compose -f docker/docker-compose.yml up -d

# Create the taxi_rides topic
./scripts/setup_kafka_topic.sh
```

Kafka UI (topic inspector) is available at http://localhost:8080 once the
containers are up.

### 5.5 Run the pipeline

Each of these runs in its own terminal, in order:

```bash
# Terminal 1 — start the Spark Structured Streaming consumer first, so it's
# ready to receive events as soon as the producer starts sending them
python streaming/spark_stream_consumer.py

# Terminal 2 — replay historical rides onto the Kafka topic as a live feed
python producer/kafka_producer.py
```

The consumer writes cleaned ride-level rows to `output/parquet/rides/` and
refreshed aggregate snapshots to `output/parquet/aggregates/` as data
arrives. Let it run for at least a few minutes so there's data to look at.

### 5.6 Train the fare-prediction model

Once some ride data exists (either from the streaming run above or the raw
dataset directly), train and persist the model:

```bash
python ml/train_model.py
```

This prints RMSE/MAE on a held-out test split and saves the fitted
pipeline to `models/fare_prediction`.

### 5.7 Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Then open the URL Streamlit prints (default `http://localhost:8501`) and
use the sidebar to navigate between pages:

| Page | What it shows |
|------|----------------|
| **Overview** | Total trips, revenue, average fare/duration, trips-per-hour and payment-type charts |
| **Location Analytics** | Top pickup/dropoff zones, with borough/zone names from `data/zone_lookup/` |
| **Ride Explorer** | Filterable table of individual cleaned rides (date range, passenger count, payment type, zone) |
| **Prediction** | Enter trip distance, passenger count, pickup hour, and zones to get a predicted fare from the trained model |
| **Streaming Monitor** | Near-real-time view of pipeline activity (trips per 5-minute window, most recent ride, manual/auto-refresh) |

If a page shows a "no data yet" warning, the streaming consumer/producer
haven't produced output yet, or (for Prediction) the model hasn't been
trained yet.

### 5.8 Run the tests

```bash
pytest
```

## 6. Team Task Distribution (suggested, 4 members)

| Member | Focus | Key Files |
|--------|-------|-----------|
| 1 — Data Engineering | Dataset acquisition, cleaning, feature engineering, Kafka producer | `data/`, `preprocessing/`, `producer/` |
| 2 — Streaming & Spark | Kafka + Structured Streaming setup, aggregations, Parquet sink | `streaming/`, `analytics/`, `docker/` |
| 3 — Machine Learning | MLlib pipeline, training, evaluation, model persistence | `ml/`, `models/` |
| 4 — Dashboard & Integration | Streamlit app, charts, live metrics, prediction UI | `dashboard/` |

Team size and split are flexible — adapt to your actual roster.

## 7. Assumptions Made While Designing This Blueprint

Documented in full in [`docs/architecture.md`](docs/architecture.md); summarized here:

1. **Dataset**: NYC TLC Yellow Taxi Trip Records (public, monthly Parquet/CSV
   files) is used as the historical source that the Kafka producer replays
   as a simulated live feed.
2. **Zones, not raw text**: The TLC dataset encodes pickup/dropoff locations
   as `LocationID` integers. A separate `taxi_zone_lookup.csv` (also
   published by TLC) is required to map IDs to human-readable zone/borough
   names — this file is included as `data/zone_lookup/`.
3. **Storage format**: Parquet is used as the single storage format for
   simplicity. Delta Lake is mentioned in the original spec as optional and
   is **not** included by default to keep the beginner-friendly scope, but
   `docs/architecture.md` notes how to add it later.
4. **Model choice**: Random Forest Regressor is the default MLlib
   algorithm (per the spec's own recommendation), with GBT/Linear
   Regression as documented alternatives in `ml/train_model.py`.
5. **Docker is optional**: included for convenience (local Kafka +
   Zookeeper) but the project should also run against any Kafka broker the
   team already has access to (e.g., a shared ITI lab cluster).
6. **Single Kafka topic**: `taxi_rides`, as specified in the source
   document.
7. **Config centralization**: environment-specific values (Kafka broker
   address, topic name, file paths) are centralized in `.env` /
   `config/config.py` rather than hardcoded, so the same code runs on any
   teammate's machine.

## 8. License

See [`LICENSE`](LICENSE).
