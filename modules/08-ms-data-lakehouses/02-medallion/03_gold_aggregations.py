# Databricks notebook source
# MAGIC %md
# MAGIC # Medallion — Gold Layer (Business Aggregations)
# MAGIC
# MAGIC **Big Data Course — UPB**
# MAGIC
# MAGIC The Gold layer contains data that is **aggregated and ready for consumption**.
# MAGIC Optimized for BI dashboards, executive reports, and feature stores.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuration and Read from Silver

# COMMAND ----------

from pyspark.sql.functions import (
    col, avg, min, max, count, round, stddev,
    percentile_approx, current_timestamp
)

# ─── CONFIGURE YOUR LAST NAME HERE ───────────────────────────────────────────
CATALOG = "maestria_bd_2026_01"
SCHEMA  = None  # <-- Change to your last name (lowercase)
VOLUME  = "datalake"
# ──────────────────────────────────────────────────────────────────────────────

# Unity Catalog volume path
VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

# Paths
SILVER_PATH      = f"{VOLUME_PATH}/medallion/silver/travel_times"
GOLD_PATH_CITY   = f"{VOLUME_PATH}/medallion/gold/city_metrics"
GOLD_PATH_ROUTES = f"{VOLUME_PATH}/medallion/gold/top_routes"

# Set default catalog and schema
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

print(f"Catalog:          {CATALOG}")
print(f"Schema:           {SCHEMA}")
print(f"Silver path:      {SILVER_PATH}")
print(f"Gold city path:   {GOLD_PATH_CITY}")
print(f"Gold routes path: {GOLD_PATH_ROUTES}")

# COMMAND ----------

# Read from Silver (Delta in the volume)
df_silver = spark.read.format("delta").load(SILVER_PATH)
print(f"Records in Silver: {df_silver.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Gold Table 1: Metrics per city
# MAGIC
# MAGIC Aggregated KPIs that an executive or business analyst needs.

# COMMAND ----------

df_city_metrics = (df_silver
    .groupBy("city")
    .agg(
        count("*").alias("total_routes"),
        round(avg("mean_travel_time_sec"), 0).alias("avg_travel_sec"),
        round(avg("mean_travel_time_sec") / 60, 1).alias("avg_travel_min"),
        round(min("mean_travel_time_sec"), 0).alias("min_travel_sec"),
        round(max("mean_travel_time_sec"), 0).alias("max_travel_sec"),
        round(stddev("mean_travel_time_sec"), 0).alias("stddev_travel_sec"),
        round(avg("upper_bound_sec") - avg("lower_bound_sec"), 0).alias("avg_uncertainty_sec"),
    )
    .withColumn("_gold_timestamp", current_timestamp())
    .orderBy("avg_travel_min")
)

df_city_metrics.show()

# COMMAND ----------

# Write Gold — city metrics
(df_city_metrics.write
    .format("delta")
    .mode("overwrite")
    .save(GOLD_PATH_CITY)
)

print(f"Gold city metrics written to: {GOLD_PATH_CITY}")

# Register as a table in Unity Catalog
GOLD_TABLE_CITY = "gold_city_metrics"
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {GOLD_TABLE_CITY}
USING DELTA
LOCATION '{GOLD_PATH_CITY}'
""")

print(f"Table registered: {CATALOG}.{SCHEMA}.{GOLD_TABLE_CITY}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Gold Table 2: Top slowest routes per city
# MAGIC
# MAGIC The 10 routes with the highest average travel time per city.

# COMMAND ----------

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

window_spec = Window.partitionBy("city").orderBy(col("mean_travel_time_sec").desc())

df_top_routes = (df_silver
    .select("city", "origin_name", "destination_name",
            "mean_travel_time_sec", "lower_bound_sec", "upper_bound_sec")
    .withColumn("rank", row_number().over(window_spec))
    .filter(col("rank") <= 10)
    .withColumn("travel_minutes", round(col("mean_travel_time_sec") / 60, 1))
    .withColumn("_gold_timestamp", current_timestamp())
)

df_top_routes.show(20, truncate=False)

# COMMAND ----------

# Write Gold — top routes
(df_top_routes.write
    .format("delta")
    .mode("overwrite")
    .save(GOLD_PATH_ROUTES)
)

print(f"Gold top routes written to: {GOLD_PATH_ROUTES}")

# Register as a table in Unity Catalog
GOLD_TABLE_ROUTES = "gold_top_routes"
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {GOLD_TABLE_ROUTES}
USING DELTA
LOCATION '{GOLD_PATH_ROUTES}'
""")

print(f"Table registered: {CATALOG}.{SCHEMA}.{GOLD_TABLE_ROUTES}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Gold queries (ready for BI)

# COMMAND ----------

# Dashboard: metrics per city
df_city = spark.read.format("delta").load(GOLD_PATH_CITY)
df_city.orderBy(col("avg_travel_min").desc()).show()

# COMMAND ----------

# Dashboard: slowest routes in Bogota
df_routes = spark.read.format("delta").load(GOLD_PATH_ROUTES)
(df_routes
    .filter(col("city") == "Bogota")
    .orderBy("rank")
    .select("rank", "origin_name", "destination_name", "travel_minutes")
    .show(truncate=False)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key takeaways for Gold
# MAGIC
# MAGIC - Business aggregations (averages, rankings, KPIs)
# MAGIC - Tables optimized for fast queries
# MAGIC - Ready to connect with Power BI, Tableau, etc.
# MAGIC - Each table has a clear business purpose
# MAGIC - Executives don't need to know about Bronze or Silver
