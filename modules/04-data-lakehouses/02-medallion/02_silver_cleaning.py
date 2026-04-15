# Databricks notebook source
# MAGIC %md
# MAGIC # Medallion — Silver Layer (Cleaning and Validation)
# MAGIC
# MAGIC **Big Data Course — UPB**
# MAGIC
# MAGIC The Silver layer takes data from Bronze and **cleans, validates, and conforms** it.
# MAGIC Silver data is reliable for analytics and data science.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Read from Bronze

# COMMAND ----------

from pyspark.sql.functions import (
    col, trim, regexp_extract, split, when, current_timestamp
)
from pyspark.sql.types import IntegerType, DoubleType

# ─── CONFIGURE THESE VARIABLES (same as Bronze) ──────────────────────────────
STORAGE_ACCOUNT = "<your_storage_account>"
CONTAINER       = "bigdata"
ACCESS_KEY      = "<your_access_key>"
# NOTE: Replace "<your_initials>_" with your initials (e.g., "jsm_" for John Smith)
# ──────────────────────────────────────────────────────────────────────────────

# Configure access to ADLS Gen2 via Access Key (same as Bronze)
spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    ACCESS_KEY
)

ADLS_BASE    = f"abfss://{CONTAINER}@{STORAGE_ACCOUNT}.dfs.core.windows.net"
BRONZE_TABLE = "<PLACEHOLDER>_medallion.bronze_travel_times"
SILVER_PATH  = f"{ADLS_BASE}/medallion/silver/travel_times"
SILVER_TABLE = "<PLACEHOLDER>_medallion.silver_travel_times"

df_bronze = spark.table(BRONZE_TABLE)
print(f"📥 Records in Bronze: {df_bronze.count()}")
df_bronze.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Silver transformations
# MAGIC
# MAGIC - Rename columns (snake_case, no spaces)
# MAGIC - Clean and cast types (STRING → INT, DOUBLE) with error handling
# MAGIC - Extract city from the source file name
# MAGIC - Remove geometries (not needed for analytics)
# MAGIC - Filter invalid records
# MAGIC - Deduplicate

# COMMAND ----------

df_silver = (df_bronze
    # Rename columns to snake_case
    .withColumnRenamed("Origin Movement ID", "origin_id")
    .withColumnRenamed("Origin Display Name", "origin_name")
    .withColumnRenamed("Destination Movement ID", "destination_id")
    .withColumnRenamed("Destination Display Name", "destination_name")
    .withColumnRenamed("Date Range", "date_range")
    .withColumnRenamed("Mean Travel Time (Seconds)", "mean_travel_time_sec")
    .withColumnRenamed("Range - Lower Bound Travel Time (Seconds)", "lower_bound_sec")
    .withColumnRenamed("Range - Upper Bound Travel Time (Seconds)", "upper_bound_sec")

    # Drop geometry columns (heavy, not needed for analytics)
    .drop("Origin Geometry", "Destination Geometry")

    # Cast types safely using try_cast (returns null on error instead of crashing)
    .withColumn("origin_id", col("origin_id").try_cast(IntegerType()))
    .withColumn("destination_id", col("destination_id").try_cast(IntegerType()))
    .withColumn("mean_travel_time_sec", col("mean_travel_time_sec").try_cast(DoubleType()))
    .withColumn("lower_bound_sec", col("lower_bound_sec").try_cast(DoubleType()))
    .withColumn("upper_bound_sec", col("upper_bound_sec").try_cast(DoubleType()))

    # Extract city from the source file name
    .withColumn("city", regexp_extract("_source_file", regexp_extract("_source_file", r"/Travel_Times%20-%20([^/]+)\.csv$", 1))

    # Clean names
    .withColumn("origin_name", trim(col("origin_name")))
    .withColumn("destination_name", trim(col("destination_name")))

    # Add Silver processing timestamp
    .withColumn("_silver_timestamp", current_timestamp())

    # Drop Bronze metadata (no longer needed)
    .drop("_ingestion_timestamp", "_source_file")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validation and filtering

# COMMAND ----------

# Count records before filtering
total_before = df_silver.count()

# Show records with null values in critical fields (for debugging)
print("🔍 Records with null values before filtering:")
df_silver.filter(
    col("origin_id").isNull() |
    col("destination_id").isNull() |
    col("mean_travel_time_sec").isNull()
).select(
    "origin_id", "destination_id", "mean_travel_time_sec",
    "origin_name", "destination_name", "city"
).show(20, truncate=False)

# Filter invalid records
df_silver_clean = (df_silver
    # Remove records where the cast failed (nulls in NOT NULL fields)
    .filter(col("origin_id").isNotNull())
    .filter(col("destination_id").isNotNull())
    .filter(col("mean_travel_time_sec").isNotNull())
    .filter(col("mean_travel_time_sec") > 0)

    # Remove duplicates
    .dropDuplicates(["origin_id", "destination_id", "city", "date_range"])
)

total_after = df_silver_clean.count()
rejected = total_before - total_after

print(f"📊 Records before cleaning: {total_before}")
print(f"✅ Valid records (Silver):   {total_after}")
print(f"❌ Rejected records:         {rejected}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Write to Silver (Delta, merge/overwrite)

# COMMAND ----------

(df_silver_clean.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("city")
    .option("overwriteSchema", "true")
    .save(SILVER_PATH)
)

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {SILVER_TABLE}
USING DELTA
LOCATION '{SILVER_PATH}'
""")

print(f"✅ Silver written to: {SILVER_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Explore Silver

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM <PLACEHOLDER>_medallion.silver_travel_times LIMIT 10

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Records per city
# MAGIC SELECT city, COUNT(*) as routes,
# MAGIC        ROUND(AVG(mean_travel_time_sec), 0) as avg_travel_sec,
# MAGIC        ROUND(AVG(mean_travel_time_sec) / 60, 1) as avg_travel_min
# MAGIC FROM <PLACEHOLDER>_medallion.silver_travel_times
# MAGIC GROUP BY city
# MAGIC ORDER BY routes DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verify data types
# MAGIC DESCRIBE <PLACEHOLDER>_medallion.silver_travel_times

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key takeaways for Silver
# MAGIC
# MAGIC - ✅ Columns renamed to snake_case
# MAGIC - ✅ Types correctly cast (INT, DOUBLE)
# MAGIC - ✅ Geometries removed (not needed)
# MAGIC - ✅ City extracted from the file name
# MAGIC - ✅ Invalid records filtered out
# MAGIC - ✅ Duplicates removed
# MAGIC - ✅ Reliable data for analytics and data science
