# Docker — run Spark without installing Java

This folder lets you run the whole project inside a container that already
has Java + PySpark, so you don't need to install a JDK locally (and on
Windows you avoid the `winutils.exe` / `HADOOP_HOME` setup entirely). Spark
runs in local mode inside the single `app` service.

## Build once

```bash
docker compose -f docker/docker-compose.yml build
```

## Run the pipeline

Run these from the project root. Each command runs a step; the project
folder is mounted, so `output/`, `models/`, and `data/stream/` created in the
container show up on your machine too.

```bash
# 1. Train the fare model (once)
docker compose -f docker/docker-compose.yml run --rm app python src/train_model.py

# 2. Start the streaming job (Terminal A)
docker compose -f docker/docker-compose.yml run --rm app python src/streaming_job.py

# 3. Start the simulated live feed (Terminal B)
docker compose -f docker/docker-compose.yml run --rm app python src/generate_stream.py

# 4. Launch the dashboard (default command) at http://localhost:8501
docker compose -f docker/docker-compose.yml up
```

Make sure the historical dataset is in `data/raw/` before training (see
`data/raw/README.md`).
