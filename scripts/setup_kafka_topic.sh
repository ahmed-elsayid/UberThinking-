#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_kafka_topic.sh
# Creates the `taxi_rides` Kafka topic used by producer/kafka_producer.py
# and streaming/spark_stream_consumer.py.
#
# Usage (against the Docker Compose broker in docker/docker-compose.yml):
#   ./scripts/setup_kafka_topic.sh
#
# Override defaults via env vars, e.g. for a shared/remote broker:
#   KAFKA_CONTAINER=my-kafka TOPIC=taxi_rides PARTITIONS=3 REPLICATION=1 \
#       ./scripts/setup_kafka_topic.sh
# ---------------------------------------------------------------------------

set -euo pipefail

KAFKA_CONTAINER="${KAFKA_CONTAINER:-uberthinking-kafka}"
TOPIC="${TOPIC:-taxi_rides}"
PARTITIONS="${PARTITIONS:-1}"
REPLICATION="${REPLICATION:-1}"
BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-localhost:9092}"

echo "Creating topic '${TOPIC}' (partitions=${PARTITIONS}, replication=${REPLICATION})..."

if docker ps --format '{{.Names}}' | grep -q "^${KAFKA_CONTAINER}$"; then
  docker exec "${KAFKA_CONTAINER}" kafka-topics \
    --create \
    --if-not-exists \
    --topic "${TOPIC}" \
    --partitions "${PARTITIONS}" \
    --replication-factor "${REPLICATION}" \
    --bootstrap-server localhost:9092

  echo "Topics currently on the broker:"
  docker exec "${KAFKA_CONTAINER}" kafka-topics --list --bootstrap-server localhost:9092
else
  echo "Container '${KAFKA_CONTAINER}' not running; falling back to a local kafka-topics.sh."
  kafka-topics.sh \
    --create \
    --if-not-exists \
    --topic "${TOPIC}" \
    --partitions "${PARTITIONS}" \
    --replication-factor "${REPLICATION}" \
    --bootstrap-server "${BOOTSTRAP_SERVER}"

  echo "Topics currently on the broker:"
  kafka-topics.sh --list --bootstrap-server "${BOOTSTRAP_SERVER}"
fi
