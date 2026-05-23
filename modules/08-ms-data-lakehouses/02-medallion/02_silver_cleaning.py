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
# MAGIC ## 1. Configuration and Read from Bronze

# COMMAND ----------

from pyspark.sql.functions import (
    col, trim, regexp_extract, when, current_timestamp, expr
)
from pyspark.sql.types import IntegerType, DoubleType

# ─── CONFIGURE YOUR LAST NAME HERE ───────────────────────────────────────────
CATALOG = "maestria_bd_2026_01"
SCHEMA  = None  # <-- Change to your last name (lowercase)
VOLUME  = "datalake"
# ──────────────────────────────────────────────────────────────────────────────

# Unity Catalog volume path
VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

# Paths
BRONZE_PATH = f"{VOLUME_PATH}/medallion/bronze/travel_times"
SILVER_PATH = f"{VOLUME_PATH}/medallion/silver/travel_times"

# Set default catalog and schema
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

print(f"Catalog:     {CATALOG}")
print(f"Schema:      {SCHEMA}")
print(f"Bronze path: {BRONZE_PATH}")
print(f"Silver path: {SILVER_PATH}")

# COMMAND ----------

# Read from Bronze (Delta in the volume)
df_bronze = spark.read.format("delta").load(BRONZE_PATH)
print(f"Records in Bronze: {df_bronze.count()}")
df_bronze.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Silver transformations
# MAGIC
# MAGIC - Rename columns (snake_case, no spaces)
# MAGIC - Clean and cast types (STRING -> INT, DOUBLE) with error handling
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

    # Cast types safely using try_cast (returns null on malformed input instead of failing)
    .withColumn("origin_id", expr("try_cast(origin_id AS INT)"))
    .withColumn("destination_id", expr("try_cast(destination_id AS INT)"))
    .withColumn("mean_travel_time_sec", expr("try_cast(mean_travel_time_sec AS DOUBLE)"))
    .withColumn("lower_bound_sec", expr("try_cast(lower_bound_sec AS DOUBLE)"))
    .withColumn("upper_bound_sec", expr("try_cast(upper_bound_sec AS DOUBLE)"))

    # Extract city from the source file name
    # File names look like: .../Travel_Times%20-%20Bogota.csv
    .withColumn("city", regexp_extract("_source_file", r"Travel_Times%20-%20(.+)\.csv", 1))

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
print("Records with null values before filtering:")
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
    # Remove records where the cast failed (nulls in critical fields)
    .filter(col("origin_id").isNotNull())
    .filter(col("destination_id").isNotNull())
    .filter(col("mean_travel_time_sec").isNotNull())
    .filter(col("mean_travel_time_sec") > 0)

    # Remove duplicates
    .dropDuplicates(["origin_id", "destination_id", "city", "date_range"])
)

total_after = df_silver_clean.count()
rejected = total_before - total_after

print(f"Records before cleaning: {total_before}")
print(f"Valid records (Silver):  {total_after}")
print(f"Rejected records:        {rejected}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Write to Silver (Delta, overwrite with partition by city)

# COMMAND ----------

(df_silver_clean.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("city")
    .option("overwriteSchema", "true")
    .save(SILVER_PATH)
)

print(f"Silver written to: {SILVER_PATH}")

# Register as a table in Unity Catalog pointing to the Delta location
SILVER_TABLE = "silver_travel_times"
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {SILVER_TABLE}
USING DELTA
LOCATION '{SILVER_PATH}'
""")

print(f"Table registered: {CATALOG}.{SCHEMA}.{SILVER_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Explore Silver

# COMMAND ----------

df_silver_verify = spark.read.format("delta").load(SILVER_PATH)
df_silver_verify.show(10)

# COMMAND ----------

# Records per city
df_silver_verify.groupBy("city").agg(
    {"*": "count", "mean_travel_time_sec": "avg"}
).withColumnRenamed("count(1)", "routes") \
 .withColumnRenamed("avg(mean_travel_time_sec)", "avg_travel_sec") \
 .orderBy(col("routes").desc()) \
 .show()

# COMMAND ----------

# Verify schema
df_silver_verify.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key takeaways for Silver
# MAGIC
# MAGIC - Columns renamed to snake_case
# MAGIC - Types correctly cast (INT, DOUBLE)
# MAGIC - Geometries removed (not needed)
# MAGIC - City extracted from the file name
# MAGIC - Invalid records filtered out
# MAGIC - Duplicates removed
# MAGIC - Reliable data for analytics and data science
