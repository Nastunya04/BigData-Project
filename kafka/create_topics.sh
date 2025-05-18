#!/bin/bash

set -euo pipefail

KAFKA_CONTAINER="kafka-server"
BROKER="kafka-server:9092"
TOPICS=("input" "processed")

echo "Waiting for Kafka to be ready..."
sleep 10

create_topic() {
  local topic="$1"
  echo "Creating topic: $topic"
  docker exec "$KAFKA_CONTAINER" kafka-topics.sh \
    --create \
    --if-not-exists \
    --bootstrap-server "$BROKER" \
    --replication-factor 1 \
    --partitions 5 \
    --topic "$topic"
}

for topic in "${TOPICS[@]}"; do
  create_topic "$topic"
done

echo "Kafka topics currently available:"
docker exec "$KAFKA_CONTAINER" kafka-topics.sh --list --bootstrap-server "$BROKER"
