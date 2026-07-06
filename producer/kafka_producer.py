"""
kafka_producer.py
------------------
Purpose:
    Reads historical taxi ride rows from data/raw/ and streams them, one
    at a time, to a Kafka topic — simulating a live feed of taxi rides
    arriving in real time (rather than replaying the whole dataset at once).

Responsibilities:
    - Read rows sequentially from the raw dataset (e.g., via pandas or a
      simple file iterator — this file should NOT depend on Spark).
    - Convert each row into a JSON message matching the schema expected by
      streaming/schema.py.
    - Publish each JSON message to the Kafka topic named in config
      (KAFKA_TOPIC).
    - Sleep for PRODUCER_DELAY_SECONDS between messages to simulate
      realistic ride arrival timing.
    - Handle basic errors (e.g., malformed rows) by logging and skipping.

Expected input:
    - File at RAW_DATA_PATH (see config/config.py).

Expected output:
    - JSON messages published to Kafka topic KAFKA_TOPIC, e.g.:
        {
          "pickup_datetime": "2024-05-01T10:05:00",
          "dropoff_datetime": "2024-05-01T10:21:00",
          "trip_distance": 6.5,
          "pickup_location_id": 142,
          "dropoff_location_id": 236,
          "fare_amount": 18.3,
          "tip_amount": 3.2,
          "passenger_count": 2,
          "payment_type": "Card"
        }

Dependencies:
    - kafka-python (KafkaProducer)
    - pandas (or csv/pyarrow) for reading raw data
    - config/config.py

Run:
    python producer/kafka_producer.py
"""

# TODO: implement producer loop:
#   1. Load config.
#   2. Open raw data file as an iterator.
#   3. For each row -> build dict -> json.dumps -> producer.send(topic, value)
#   4. time.sleep(PRODUCER_DELAY_SECONDS)
