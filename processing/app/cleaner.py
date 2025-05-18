from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, date_format, sha2, concat_ws
from pyspark.sql.types import StructType, StringType, BooleanType, LongType

spark = SparkSession.builder \
    .appName("KafkaCleanerProcessor") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType() \
    .add("page_id", LongType()) \
    .add("page_title", StringType()) \
    .add("performer", StructType()
         .add("user_text", StringType())
         .add("user_id", LongType())
         .add("user_is_bot", BooleanType())) \
    .add("meta", StructType()
         .add("domain", StringType())
         .add("dt", StringType()))

df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-server:9092") \
    .option("subscribe", "input") \
    .option("startingOffsets", "latest") \
    .load()

df_json = df_raw.selectExpr("CAST(value AS STRING) AS json_str") \
    .select(from_json(col("json_str"), schema).alias("data"))

df_parsed = df_json.select(
    col("data.page_id").alias("page_id"),
    col("data.page_title").alias("page_title"),
    col("data.performer.user_text").alias("user_name"),
    col("data.performer.user_id").alias("user_id"),
    col("data.performer.user_is_bot").alias("is_bot"),
    col("data.meta.domain").alias("domain"),
    col("data.meta.dt").alias("created_at")
)

required_columns = ["page_id", "page_title", "user_name", "user_id", "domain", "created_at"]
df_filtered = df_parsed.dropna(subset=required_columns)

df_enriched = df_filtered.withColumn(
    "date_hour", date_format("created_at", "yyyy-MM-dd-HH")
)

df_enriched.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", False) \
    .option("numRows", 20) \
    .start()

df_out = df_enriched.withColumn(
    "key", sha2(concat_ws(":", col("user_id")), 256)
).selectExpr("CAST(key AS STRING) as key", "to_json(struct(*)) AS value")

df_out.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-server:9092") \
    .option("topic", "processed") \
    .option("checkpointLocation", "/tmp/checkpoints/cleaner_job") \
    .outputMode("append") \
    .start() \
    .awaitTermination()
