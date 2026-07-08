# A self-contained environment for running UberThinking's Spark code.
# PySpark bundles Spark itself, so all we need is Python + a JDK. Running in
# this Linux container also avoids the Windows winutils/HADOOP_HOME setup.

FROM python:3.10-slim

# Java 17 runtime, required by Spark 3.5.
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies from pyproject.toml. The full project is mounted at
# runtime (see docker-compose.yml), so live edits don't need a rebuild — this
# copy is only what pip needs to resolve and install the dependencies.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8501

# Default command: launch the dashboard. Override it to run other scripts,
# e.g. `docker compose ... run --rm app python train_model.py`.
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0"]
