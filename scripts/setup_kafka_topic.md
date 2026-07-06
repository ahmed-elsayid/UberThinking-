# scripts/setup_kafka_topic.md

Purpose:
    Documents (rather than hardcodes) the one-time setup step of creating
    the `taxi_rides` Kafka topic, so it's not buried in application code.

What to do (guidance, not a ready-to-run script):
    1. Ensure Kafka + Zookeeper are running (see docker/docker-compose.yml
       or your shared broker).
    2. Use the Kafka CLI (kafka-topics.sh / kafka-topics.bat, or the
       equivalent `docker exec` call into the Kafka container) to create a
       topic named `taxi_rides` with a reasonable number of partitions
       (e.g. 1 for local dev, more for parallel consumers later) and a
       replication factor appropriate to your broker count (1 for a single
       local broker).
    3. Verify the topic exists by listing topics.

Why a topic-creation script/doc instead of relying on auto-create:
    Being explicit about partitions/replication avoids surprises later if
    the team scales the consumer side (e.g. adding parallel streaming
    queries).

Consider converting this into an actual `setup_kafka_topic.sh` once the
team has finalized its Kafka deployment approach (Docker vs. shared
cluster), since the exact CLI invocation depends on that choice.
