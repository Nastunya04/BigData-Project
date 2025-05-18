from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StringType, BooleanType

import sys
import logging

# ========== Logging ==========
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("KafkaToCassandraWriter")

logger.info("Starting Spark Streaming Application...")

# ========== Spark Session ==========
spark = SparkSession.builder \
    .appName("KafkaToCassandraWriter") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
logger.info("Spark session created.")

# ========== Schema ==========
schema = StructType() \
    .add("page_id", StringType()) \
    .add("page_title", StringType()) \
    .add("user_name", StringType()) \
    .add("user_id", StringType()) \
    .add("is_bot", BooleanType()) \
    .add("domain", StringType()) \
    .add("created_at", StringType()) \
    .add("date_hour", StringType())

logger.info("Schema defined.")

# ========== Read from Kafka ==========
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-server:9092") \
    .option("subscribe", "processed") \
    .option("startingOffsets", "earliest") \
    .load()

logger.info("Kafka stream initialized.")

df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("created_at", to_timestamp("created_at"))

logger.info("Kafka data parsed.")

# ========== Split for Writing ==========
df_common = df_parsed.drop("is_bot", "date_hour")
df_time = df_parsed.drop("is_bot")

logger.info("Dataframes split for writing to respective tables.")

# ========== ForeachBatch Functions ==========
def log_and_write(df, batch_id, table_name):
    count = df.count()
    logger.info(f"[{table_name}] Writing batch {batch_id} with {count} rows.")
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .option("keyspace", "wiki") \
        .option("table", table_name) \
        .mode("append") \
        .save()

# ========== Start Streams ==========
logger.info("Starting write stream: pages_by_id")
query_id = df_common.writeStream \
    .foreachBatch(lambda df, id: log_and_write(df, id, "pages_by_id")) \
    .option("checkpointLocation", "/tmp/checkpoints/pages_by_id") \
    .outputMode("append") \
    .start()

logger.info("Starting write stream: pages_by_user")
query_user = df_common.writeStream \
    .foreachBatch(lambda df, id: log_and_write(df, id, "pages_by_user")) \
    .option("checkpointLocation", "/tmp/checkpoints/pages_by_user") \
    .outputMode("append") \
    .start()

logger.info("Starting write stream: pages_by_domain")
query_domain = df_common.writeStream \
    .foreachBatch(lambda df, id: log_and_write(df, id, "pages_by_domain")) \
    .option("checkpointLocation", "/tmp/checkpoints/pages_by_domain") \
    .outputMode("append") \
    .start()

logger.info("Starting write stream: pages_by_time")
query_time = df_time.writeStream \
    .foreachBatch(lambda df, id: log_and_write(df, id, "pages_by_time")) \
    .option("checkpointLocation", "/tmp/checkpoints/pages_by_time") \
    .outputMode("append") \
    .start()

# ========== Await Termination ==========
logger.info("All write streams started. Awaiting termination...")
query_id.awaitTermination()
query_user.awaitTermination()
query_domain.awaitTermination()
query_time.awaitTermination()
