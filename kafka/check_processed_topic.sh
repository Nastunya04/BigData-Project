#!/bin/bash

docker exec -it kafka-server kafka-console-consumer.sh \
  --bootstrap-server kafka-server:9092 \
  --topic processed \
  --from-beginning
