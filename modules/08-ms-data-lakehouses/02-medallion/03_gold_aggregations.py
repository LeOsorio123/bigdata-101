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
# MAGIC ## 1. Read from Silver

# COMMAND ----------

from pyspark.sql.functions import (
    col, avg, min, max, count, round, stddev,
    percentile_approx, current_timestamp
)

# ─── CONFIGURE THESE VARIABLES (same as Bronze/Silver) ───────────────────────
STORAGE_ACCOUNT = "<your_storage_account>"
CONTAINER       = "bigdata"
ACCESS_KEY      = "<your_access_key>"
# In production use: ACCESS_KEY = dbutils.secrets.get(scope="adls-scope", key="storage-key")
# ──────────────────────────────────────────────────────────────────────────────

spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    ACCESS_KEY
)

ADLS_BASE        = f"abfss://{CONTAINER}@{STORAGE_ACCOUNT}.dfs.core.windows.net"
SILVER_TABLE     = "medallion.silver_travel_times"
GOLD_PATH_CITY   = f"{ADLS_BASE}/medallion/gold/city_metrics"
GOLD_PATH_ROUTES = f"{ADLS_BASE}/medallion/gold/top_routes"

df_silver = spark.table(SILVER_TABLE)
print(f"📥 Records in Silver: {df_silver.count()}")

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

spark.sql(f"""
CREATE TABLE IF NOT EXISTS medallion.gold_city_metrics
USING DELTA
LOCATION '{GOLD_PATH_CITY}'
""")

print("✅ Gold table: medallion.gold_city_metrics")

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

spark.sql(f"""
CREATE TABLE IF NOT EXISTS medallion.gold_top_routes
USING DELTA
LOCATION '{GOLD_PATH_ROUTES}'
""")

print("✅ Gold table: medallion.gold_top_routes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Gold queries (ready for BI)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Dashboard: metrics per city
# MAGIC SELECT city, total_routes, avg_travel_min,
# MAGIC        min_travel_sec, max_travel_sec, avg_uncertainty_sec
# MAGIC FROM medallion.gold_city_metrics
# MAGIC ORDER BY avg_travel_min DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Dashboard: slowest routes in Bogota
# MAGIC SELECT rank, origin_name, destination_name, travel_minutes
# MAGIC FROM medallion.gold_top_routes
# MAGIC WHERE city = 'Bogota'
# MAGIC ORDER BY rank

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key takeaways for Gold
# MAGIC
# MAGIC - ✅ Business aggregations (averages, rankings, KPIs)
# MAGIC - ✅ Tables optimized for fast queries
# MAGIC - ✅ Ready to connect with Power BI, Tableau, etc.
# MAGIC - ✅ Each table has a clear business purpose
# MAGIC - ✅ Executives don't need to know about Bronze or Silver
