# Databricks notebook source
# MAGIC %md
# MAGIC # Silver: limpieza y validación

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

bronze = spark.read.format("delta").load(PATH_BRONZE_TRIPS)

trips = bronze.withColumn(
    "trip_duration_min",
    (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime")) / 60.0,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reglas de calidad

# COMMAND ----------

rules = {
    "valid_distance":   F.col("trip_distance") > 0,
    "valid_fare":       F.col("fare_amount") >= 0,
    "valid_total":      F.col("total_amount") > 0,
    "valid_passengers": F.col("passenger_count").between(1, 8),
    "valid_dropoff":    F.col("tpep_dropoff_datetime") > F.col("tpep_pickup_datetime"),
    "valid_duration":   F.col("trip_duration_min").between(1, 360),
}

is_valid = None
for expr in rules.values():
    is_valid = expr if is_valid is None else (is_valid & expr)

# COMMAND ----------

tagged = trips
for name, expr in rules.items():
    tagged = tagged.withColumn(name, expr)

valid_df = tagged.filter(is_valid).drop(*rules.keys())
rejected_df = tagged.filter(~is_valid).withColumn("rejected_at", F.current_timestamp())

# COMMAND ----------

(
    valid_df.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .save(PATH_SILVER_TRIPS)
)

(
    rejected_df.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .save(PATH_SILVER_REJECTED)
)

# COMMAND ----------

total_bronze = bronze.count()
total_silver = spark.read.format("delta").load(PATH_SILVER_TRIPS).count()
total_rejected = spark.read.format("delta").load(PATH_SILVER_REJECTED).count()

print(f"Bronze total:    {total_bronze:>12,}")
print(f"Silver válidos:  {total_silver:>12,}  ({100 * total_silver / total_bronze:.2f}%)")
print(f"Silver rechazos: {total_rejected:>12,}  ({100 * total_rejected / total_bronze:.2f}%)")
