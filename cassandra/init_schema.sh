#!/bin/bash

set -e

MAX_RETRIES=20
RETRY_INTERVAL=5
RETRY_COUNT=0

echo "Checking if Cassandra is ready..."

while ! docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES;" >/dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "  Cassandra not ready yet... attempt $RETRY_COUNT/$MAX_RETRIES"
  if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
    echo "Cassandra did not become ready in time."
    exit 1
  fi
  sleep "$RETRY_INTERVAL"
done

echo "Cassandra is up. Proceeding with initialization..."

echo "Copying init.cql into Cassandra container..."
docker cp ./cassandra/init.cql cassandra:/init.cql

echo "Running init.cql inside Cassandra..."
docker exec -it cassandra cqlsh -f /init.cql

echo "init.cql executed successfully."

echo "Verifying created tables in keyspace 'wiki'..."
docker exec -it cassandra cqlsh -e "USE wiki; DESCRIBE TABLES;"