from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, collect_list, desc, date_trunc, lit
from datetime import datetime, timedelta

print("\n========== Starting Spark Session ==========")
spark = SparkSession.builder \
    .appName("Precomputed Reports") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.sql.extensions", "com.datastax.spark.connector.CassandraSparkExtensions") \
    .config("spark.sql.catalog.livy", "com.datastax.spark.connector.datasource.CassandraCatalog") \
    .config("spark.sql.sources.useV1SourceList", "cassandra") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

print("\n========== Reading from pages_by_time ==========")
df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="pages_by_time", keyspace="wiki") \
    .load()

now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
end_time = now - timedelta(hours=1)
start_time = end_time - timedelta(hours=6)

print(f"\n========== Filtering from {start_time} to {end_time} ==========")
df = df.filter((col("created_at") >= start_time) & (col("created_at") < end_time))

print("\n========== Writing domain_hour_stats ==========")
df_hourly = df.withColumn("hour", date_trunc("hour", "created_at"))
df_hourly.groupBy("hour", "domain") \
    .agg(count("*").alias("count")) \
    .write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="domain_hour_stats", keyspace="wiki") \
    .mode("append") \
    .save()
print("domain_hour_stats written")

print("\n========== Writing bot_domain_stats ==========")
df.filter(col("is_bot") == True) \
    .groupBy("domain") \
    .agg(count("*").alias("created_by_bots")) \
    .withColumn("time_start", lit(start_time.strftime("%Y-%m-%d %H:%M:%S"))) \
    .withColumn("time_end", lit(end_time.strftime("%Y-%m-%d %H:%M:%S"))) \
    .write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="bot_domain_stats", keyspace="wiki") \
    .mode("append") \
    .save()
print("bot_domain_stats written")

print("\n========== Writing top_users_stats ==========")
df.groupBy("user_id", "user_name") \
    .agg(collect_list("page_title").alias("page_titles"), count("*").alias("total")) \
    .orderBy(desc("total")) \
    .limit(20) \
    .withColumn("time_start", lit(start_time.strftime("%Y-%m-%d %H:%M:%S"))) \
    .withColumn("time_end", lit(end_time.strftime("%Y-%m-%d %H:%M:%S"))) \
    .write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="top_users_stats", keyspace="wiki") \
    .mode("append") \
    .save()
print("top_users_stats written")

print("\n========== All reports generated successfully ==========")
