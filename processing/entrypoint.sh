#!/bin/bash
set -e

echo "Waiting for Cassandra..."
sleep 10  # або healthcheck якщо хочеш краще

echo "Running batch_reports.py..."
python /opt/app/batch_reports.py
