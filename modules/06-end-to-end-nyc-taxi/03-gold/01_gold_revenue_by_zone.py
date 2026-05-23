# Databricks notebook source
# MAGIC %md
# MAGIC # Gold: revenue por zona

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

enriched = spark.read.format("delta").load(PATH_SILVER_TRIPS_ENRICHED)

# COMMAND ----------

revenue = (
    enriched
    .filter(F.col("pickup_zone").isNotNull())
    .groupBy("pickup_borough", "pickup_zone", "PULocationID")
    .agg(
        F.count("*").alias("total_trips"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        F.round(F.avg("total_amount"), 2).alias("avg_fare"),
        F.round(F.sum("tip_amount"), 2).alias("total_tips"),
        F.round(F.avg("tip_rate") * 100, 2).alias("avg_tip_pct"),
        F.round(F.avg("trip_distance"), 2).alias("avg_distance_mi"),
        F.round(F.avg("trip_duration_min"), 2).alias("avg_duration_min"),
    )
)

# COMMAND ----------

(
    revenue.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .save(PATH_GOLD_REVENUE_BY_ZONE)
)

print(f"✓ Gold revenue by zone escrito en {PATH_GOLD_REVENUE_BY_ZONE}")

# COMMAND ----------

display(
    spark.read.format("delta").load(PATH_GOLD_REVENUE_BY_ZONE)
    .orderBy(F.desc("total_revenue"))
    .limit(20)
)
