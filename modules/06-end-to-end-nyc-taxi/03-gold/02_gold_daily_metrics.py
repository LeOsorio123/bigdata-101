# Databricks notebook source
# MAGIC %md
# MAGIC # Gold: métricas diarias

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

enriched = spark.read.format("delta").load(PATH_SILVER_TRIPS_ENRICHED)

# COMMAND ----------

daily = (
    enriched
    .groupBy("pickup_date")
    .agg(
        F.count("*").alias("total_trips"),
        F.round(F.sum("total_amount"), 2).alias("total_revenue"),
        F.round(F.avg("total_amount"), 2).alias("avg_fare"),
        F.round(F.avg("trip_distance"), 2).alias("avg_distance_mi"),
        F.round(F.avg("trip_duration_min"), 2).alias("avg_duration_min"),
        F.round(F.avg("avg_speed_mph"), 2).alias("avg_speed_mph"),
        F.round(F.sum("tip_amount"), 2).alias("total_tips"),
        F.round(F.avg("tip_rate") * 100, 2).alias("avg_tip_pct"),
        F.countDistinct("PULocationID").alias("unique_pickup_zones"),
    )
    .orderBy("pickup_date")
)

# COMMAND ----------

(
    daily.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .save(PATH_GOLD_DAILY_METRICS)
)

print(f"✓ Gold daily metrics escrito en {PATH_GOLD_DAILY_METRICS}")

# COMMAND ----------

display(
    spark.read.format("delta").load(PATH_GOLD_DAILY_METRICS)
    .orderBy(F.desc("pickup_date"))
    .limit(30)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Días anómalos (z-score > 2)

# COMMAND ----------

from pyspark.sql import Window

daily_df = spark.read.format("delta").load(PATH_GOLD_DAILY_METRICS)

stats = daily_df.agg(
    F.avg("total_trips").alias("avg_trips"),
    F.stddev("total_trips").alias("sd_trips"),
).first()

anomalies = (
    daily_df
    .withColumn("z_score", F.round((F.col("total_trips") - stats["avg_trips"]) / stats["sd_trips"], 2))
    .filter(F.abs(F.col("z_score")) > 2)
    .orderBy("z_score")
)

display(anomalies.select("pickup_date", "total_trips", "z_score"))
