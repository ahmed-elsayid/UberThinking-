# 🚕 TaxiPulse — Real-Time Ride Intelligence using Apache Spark

TaxiPulse is a real-time analytics and fare-prediction platform built on the
Apache Spark ecosystem. It simulates a live taxi-dispatch data feed (in the
style of Uber/Careem), processes it through Kafka and Spark Structured
Streaming, stores curated results as Parquet, trains a fare-prediction model
with Spark MLlib, and surfaces everything in an interactive Streamlit
dashboard.

This repository is a **project blueprint**: every file exists with the
correct name, location, and responsibility, but contains guidance comments
instead of implementation. Use it as a scaffold to build the working system.

---

## 1. Business Problem

A ride-hailing operator needs to answer, in near real time:

- Where is rider demand increasing right now?
- Which pickup/dropoff zones are busiest?
- What is current revenue and average fare?
- How long are rides taking?
- Can we estimate a fare *before* the ride starts?

TaxiPulse continuously ingests ride events, processes and aggregates them,
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
TaxiPulse/
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

## 5. Getting Started (once implemented)

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd TaxiPulse

# 2. Create a virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Copy environment config
cp .env.example .env

# 4. Start Kafka locally (optional, via Docker)
docker compose -f docker/docker-compose.yml up -d

# 5. Run the producer (in one terminal)
python producer/kafka_producer.py

# 6. Run the Spark streaming consumer (in another terminal)
python streaming/spark_stream_consumer.py

# 7. Train the fare-prediction model
python ml/train_model.py

# 8. Launch the dashboard
streamlit run dashboard/app.py
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
