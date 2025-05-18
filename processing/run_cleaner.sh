#!/bin/bash

docker exec -it spark-master spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.executor.cores=1 \
  --conf spark.executor.memory=1G \
  --conf spark.cores.max=1 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 \
  /opt/app/cleaner.py
