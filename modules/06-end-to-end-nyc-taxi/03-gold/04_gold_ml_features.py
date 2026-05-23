# Databricks notebook source
# MAGIC %md
# MAGIC # ML Features: predicción de duración de viaje

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

enriched = spark.read.format("delta").load(PATH_SILVER_TRIPS_ENRICHED)

# COMMAND ----------

features = (
    enriched
    .filter(F.col("pickup_borough").isNotNull())
    .filter(F.col("dropoff_borough").isNotNull())
    .filter(F.col("trip_duration_min").between(2, 120))
    .filter(F.col("trip_distance").between(0.2, 50))
    .select(
        F.col("trip_duration_min").alias("target_duration_min"),
        "PULocationID", "DOLocationID",
        "pickup_borough", "dropoff_borough",
        "pickup_hour", "pickup_dayofweek",
        F.col("is_weekend").cast("int").alias("is_weekend"),
        F.col("is_rush_hour").cast("int").alias("is_rush_hour"),
        "passenger_count", "trip_distance", "RatecodeID",
        F.col("tpep_pickup_datetime").alias("pickup_ts"),
        "pickup_date",
    )
)

# COMMAND ----------

(
    features.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .save(PATH_ML_FEATURES)
)

print(f"✓ ML features escrito en {PATH_ML_FEATURES}")

# COMMAND ----------

display(
    spark.read.format("delta").load(PATH_ML_FEATURES)
    .agg(
        F.count("*").alias("rows"),
        F.round(F.avg("target_duration_min"), 2).alias("avg_duration"),
        F.round(F.stddev("target_duration_min"), 2).alias("sd_duration"),
        F.round(F.avg("trip_distance"), 2).alias("avg_distance"),
    )
)
