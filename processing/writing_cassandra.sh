#!/bin/bash

set -e

echo "Running Spark Streaming Job: write_to_cassandra.py"

docker exec -it spark-master spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.executor.cores=1 \
  --conf spark.executor.memory=1G \
  --conf spark.cores.max=1 \
  --conf spark.sql.shuffle.partitions=1 \
  --conf spark.executor.heartbeatInterval=60s \
  --conf spark.network.timeout=600s \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.2.0 \
  /opt/app/write_to_cassandra.py
