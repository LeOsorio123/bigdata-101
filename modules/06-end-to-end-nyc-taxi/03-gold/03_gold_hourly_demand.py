# Databricks notebook source
# MAGIC %md
# MAGIC # Gold: demanda por hora y zona

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

enriched = spark.read.format("delta").load(PATH_SILVER_TRIPS_ENRICHED)

# COMMAND ----------

hourly = (
    enriched
    .filter(F.col("pickup_zone").isNotNull())
    .groupBy("pickup_borough", "pickup_zone", "pickup_hour", "pickup_dayofweek", "is_weekend", "is_rush_hour")
    .agg(
        F.count("*").alias("trips"),
        F.round(F.avg("total_amount"), 2).alias("avg_fare"),
        F.round(F.avg("avg_speed_mph"), 2).alias("avg_speed_mph"),
    )
)

# COMMAND ----------

(
    hourly.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .save(PATH_GOLD_HOURLY_DEMAND)
)

print(f"✓ Gold hourly demand escrito en {PATH_GOLD_HOURLY_DEMAND}")

# COMMAND ----------

display(
    spark.read.format("delta").load(PATH_GOLD_HOURLY_DEMAND)
    .filter(F.col("is_rush_hour") == True)
    .groupBy("pickup_zone", "pickup_hour")
    .agg(F.sum("trips").alias("trips"))
    .orderBy(F.desc("trips"))
    .limit(10)
)
