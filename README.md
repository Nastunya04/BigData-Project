# Real-Time Wikipedia Page Tracking System

This project implements a full data pipeline for ingesting, processing, storing, and querying Wikipedia page creation events using Kafka, Spark, Cassandra, and FastAPI.

---

## Project Structure

```
.
├── api/                      # REST API with FastAPI
│   └── app/                  # API logic and models
├── cassandra/               # Init schema and CQL script
├── jars/                    # Required Cassandra connector JARs
├── kafka/                   # Kafka topic management scripts
├── processing/              # Spark streaming logic
│   └── app/                 # Spark jobs
├── producer/                # Wikimedia Kafka producer
├── docker-compose.yml       # Multi-service orchestration
```

---

## How to Run the System

### 1. Start Core Services

```bash
docker-compose up -d cassandra zookeeper-server kafka-server spark-master spark-worker
```

### 2. Initialize Cassandra Schema

```bash
sh cassandra/init_schema.sh
```

### 3. Create Kafka Topics

```bash
sh kafka/create_topics.sh
```

### 4. Launch Wikimedia Kafka Producer

```bash
docker-compose up -d wikimedia-producer
```

### 5. (Optional) Inspect Kafka Input Topic

```bash
sh kafka/check_input_topic.sh
```

### 6. Run Spark Cleaner Job (Kafka → Kafka)

```bash
sh processing/run_cleaner.sh
```

### 7. (Optional) Inspect Kafka Processed Topic

```bash
sh kafka/check_processed_topic.sh
```

### 8. Run Spark Writer Job (Kafka → Cassandra)

```bash
sh processing/writing_cassandra.sh
```

### 9. Start REST API

```bash
docker-compose up -d rest-api
```

---

## Verify Cassandra Tables

```bash
docker exec -it cassandra cqlsh
USE wiki;
```

You can run the following queries to confirm:

```sql
-- Lookup by page ID
SELECT * FROM pages_by_id LIMIT 10;
SELECT * FROM pages_by_id WHERE page_id = '16842590';

-- Pages created by a user
SELECT * FROM pages_by_user LIMIT 10;
SELECT * FROM pages_by_user WHERE user_id = '1234';

-- Domain-specific data
SELECT * FROM pages_by_domain LIMIT 10;
SELECT COUNT(*) FROM pages_by_domain WHERE domain = 'en.wikipedia.org';

-- Filter by time partition
SELECT * FROM pages_by_time LIMIT 10;
SELECT * FROM pages_by_time WHERE date_hour = '2024-12-01-14';
```

---

## API Access

Once `rest-api` is running, open:

```
http://localhost:8000/docs
```

To interact with endpoints like:
- `/domains/`
- `/pages/user/{user_id}`
- `/stats/time-range/`
- etc.
