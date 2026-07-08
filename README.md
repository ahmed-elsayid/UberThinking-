# 🚕 UberThinking — Real-Time Taxi Analytics with Apache Spark

UberThinking is a beginner-friendly analytics project built on Apache Spark.
It simulates a live feed of NYC taxi rides, processes it with **Spark
Structured Streaming**, trains a fare-prediction model with **Spark MLlib**,
and shows everything in a **Streamlit** dashboard.

There is **no Kafka** — the live feed is simulated by writing files into a
folder that Spark's Structured Streaming *file source* reads. This keeps the
focus on Spark itself. Docker is provided but **optional** (see below): it
gives you a ready-made Spark environment so you don't have to install Java.

## What it teaches

- **Spark DataFrames** — cleaning and feature engineering (`src/transforms.py`)
- **Spark SQL** — data exploration in `src/train_model.py`
- **Structured Streaming** — file-source streaming job (`src/streaming_job.py`)
- **Spark MLlib** — offline model training (`src/train_model.py`)
- **Streamlit** — a 3-page dashboard (`dashboard/`)

## Project structure

```text
UberThinking/
├── src/                 All the runnable Python modules
│   ├── config.py            Settings, paths, and the SparkSession builder
│   ├── transforms.py        Ride schema + cleaning/feature engineering (shared)
│   ├── generate_stream.py   Simulates the live feed (writes files, no Kafka)
│   ├── streaming_job.py     Structured Streaming: watches files -> cleans -> Parquet
│   ├── train_model.py       Trains the fare model once on historical data
│   └── predict.py           Loads the model to predict a fare
├── docker/              Optional: run everything in a Spark-ready container
├── dashboard/
│   ├── app.py                   Page 1: Dashboard (KPIs + live ride count)
│   └── pages/
│       ├── 1_Analytics.py       Page 2: charts
│       └── 2_Prediction.py      Page 3: fare prediction
├── data/
│   ├── raw/             Historical NYC taxi dataset (you download this)
│   ├── stream/          Generated live-feed files (auto-created)
│   └── zone_lookup/     LocationID -> zone name lookup
├── output/rides/        Streaming output (auto-created)
├── models/fare_model/   Trained model (auto-created)
└── tests/               A small unit test
```

## How the pieces connect

```text
data/raw (historical) ──► src/generate_stream.py ──► data/stream/*.parquet
   (or drop your own .csv / .parquet into data/stream/)    │
                                                           ▼
                                    src/streaming_job.py (Structured Streaming)
                                                           │
                                                           ▼
                                                 output/rides/*.parquet
                                                           │
                        ┌──────────────────────────────────┤
                        ▼                                  ▼
              dashboard/ (Streamlit)      src/train_model.py ──► models/fare_model
```

The streaming job watches `data/stream/` for new `.csv` or `.parquet` files.
Drop a file in and it gets streamed; an empty folder just waits (no crash).

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies (from pyproject.toml)
pip install -e .

# 3. (optional) copy the env template
cp .env.example .env
```

### Windows note

PySpark needs `winutils.exe` + `hadoop.dll` on Windows. Download them for
Hadoop 3.3.x (e.g. from github.com/cdarlint/winutils), put them in
`C:\hadoop\bin\`, and set `HADOOP_HOME=C:\hadoop` in `.env`. Also set
`JAVA_HOME` to a Java 11 or 17 JDK. `src/config.py` applies both automatically.

### Get the data

1. Download one month of NYC TLC "Yellow Taxi Trip Records" (Parquet) into
   `data/raw/` (see `data/raw/README.md`).
2. `data/zone_lookup/taxi_zone_lookup.csv` is already included.

## Run it

Train the model once, then run the streaming feed and dashboard together.

Run these from the project root.

```bash
# 1. Train the fare model (one time, uses data/raw)
python src/train_model.py

# 2. Terminal A — start the streaming job (waits for files in data/stream/)
python src/streaming_job.py

# 3. Terminal B — start the simulated live feed
python src/generate_stream.py

# 4. Terminal C — open the dashboard
streamlit run dashboard/app.py
```

Instead of (or alongside) step 3, you can just **drop your own `.csv` or
`.parquet` files into `data/stream/`** — the streaming job picks them up
automatically. Dropped files need the same columns `generate_stream.py`
produces (see `row_to_message` in `src/generate_stream.py`).

Then open http://localhost:8501 and use the sidebar:

| Page | Shows |
|------|-------|
| **Dashboard** | Total Trips, Total Revenue, Average Fare, Avg Trip Duration, Live Incoming Rides |
| **Analytics** | Trips per hour, payment types, top pickup zones |
| **Prediction** | Estimated fare for a trip you describe |

Click **Refresh** on the Dashboard to see new rides and the live incoming count.

## Run it with Docker (optional)

If you'd rather not install Java locally, run everything in a container that
already has Java + PySpark. See [`docker/README.md`](docker/README.md):

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm app python src/train_model.py
docker compose -f docker/docker-compose.yml up        # dashboard at :8501
```

## Tests

```bash
pytest
```

## License

See [`LICENSE`](LICENSE).
