# Docker (Optional Local Dev Environment)

This folder is for spinning up Kafka locally so you don't need a shared
cluster during development.

**Status:** placeholder — see `docker-compose.yml` for what needs to be
defined.

If your ITI lab already provides a Kafka broker, you can skip Docker
entirely and just point `KAFKA_BOOTSTRAP_SERVERS` in `.env` at that broker.
