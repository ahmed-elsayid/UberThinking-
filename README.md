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

### 5.0 Quick start — run the whole app

Once you've done the one-time **Setup** (5.2), **Windows notes** (5.2a) and
**data download** (5.3), this is the full end-to-end run. Activate the venv
first (`.venv\Scripts\activate` on Windows), then, from the project root:

```bash
# 1. Start Kafka (Kafka + Zookeeper + Kafka UI) in the background
docker compose -f docker/docker-compose.yml up -d

# 2. Terminal A — Spark Structured Streaming consumer (start this FIRST)
python streaming/spark_stream_consumer.py

# 3. Terminal B — replay historical rides onto Kafka as a live feed
python producer/kafka_producer.py

# 4. (after a minute or two of data) Terminal C — train the fare model
python ml/train_model.py

# 5. Terminal D — launch the dashboard
streamlit run dashboard/app.py
```

> On Windows PowerShell each `python`/`streamlit` command runs in its own
> terminal window and stays in the foreground — open a new terminal for each
> step rather than chaining them. Spark takes ~30–60s to boot on the first
> micro-batch; that's normal.

**How to see the output:**

| What | Where |
|------|-------|
| **Dashboard** (all charts, KPIs, prediction, live monitor) | http://localhost:8501 |
| **Kafka UI** (watch raw `taxi_rides` messages arrive) | http://localhost:8080 |
| Cleaned ride-level data on disk | `output/parquet/rides/` |
| Aggregate metric snapshots on disk | `output/parquet/aggregates/` |
| Trained model + printed RMSE/MAE | `models/fare_prediction` |

Steps 2–5 are detailed individually in 5.4–5.7 below.

### 5.1 Prerequisites

- Python 3.10 or 3.11
- Java 11 (required by PySpark)
- Docker + Docker Compose (optional — only needed if you don't already
  have a Kafka broker to point at)
- **Windows only:** see 5.2a below before running anything that starts
  Spark — PySpark needs a Hadoop helper binary that Windows doesn't ship.

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

### 5.2a Windows setup notes (winutils.exe)

PySpark bundles Hadoop client libraries that, on Windows, need
`winutils.exe` and `hadoop.dll` to work — without them, any script that
creates a `SparkSession` (the streaming consumer, `ml/train_model.py`, the
dashboard's Prediction page) fails during `SparkContext` init with
`HADOOP_HOME and hadoop.home.dir are unset`. This happens before Spark
ever touches Kafka, so it can look like a Kafka problem when it isn't.

To fix it:

1. Download the `winutils.exe` and `hadoop.dll` matching Hadoop 3.3.x from
   a trusted mirror, e.g. https://github.com/cdarlint/winutils (pick the
   `hadoop-3.3.4` or `hadoop-3.3.5` folder — either works with PySpark 3.5.1).
2. Put both files in a folder like `C:\hadoop\bin\`.
3. Set `HADOOP_HOME=C:\hadoop` in your `.env` file (this repo's
   `config/config.py` picks it up automatically and adds `%HADOOP_HOME%\bin`
   to `PATH` before Spark starts — no manual system-wide env var needed).
4. Also copy `hadoop.dll` into `C:\Windows\System32` if you still see
   `UnsatisfiedLinkError` after step 3.

`config/config.py` also automatically points `PYSPARK_PYTHON` /
`PYSPARK_DRIVER_PYTHON` at your venv's `python.exe`, which fixes the
related `Missing Python executable 'python3'` warning.

### 5.3 Get the data

1. Download one month of NYC TLC "Yellow Taxi Trip Records" (Parquet or
   CSV) from the official TLC Trip Record Data page and place it under
   `data/raw/` (see `data/raw/README.md`). Point `RAW_DATA_PATH` in `.env`
   at the file if the name differs from the default.
2. Download `taxi_zone_lookup.csv` (also published by TLC) into
   `data/zone_lookup/` (see `data/zone_lookup/README.md`).

### 5.4 Start Kafka

Use the bundled Docker Compose setup (Kafka + Zookeeper + Kafka UI), or
point at any Kafka broker you already have:

```bash
docker compose -f docker/docker-compose.yml up -d
```

The `taxi_rides` topic is created automatically the first time the producer
sends to it (`KAFKA_AUTO_CREATE_TOPICS_ENABLE=true` in the compose file), so
there is no separate topic-creation step. `scripts/setup_kafka_topic.md`
documents how to create it explicitly if you'd rather not rely on
auto-create.

Kafka UI (topic inspector) is available at http://localhost:8080 once the
containers are up. Stop the stack later with:

```bash
docker compose -f docker/docker-compose.yml down
```

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
