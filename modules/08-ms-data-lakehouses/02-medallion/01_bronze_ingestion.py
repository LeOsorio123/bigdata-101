# Databricks notebook source
# MAGIC %md
# MAGIC # Medallion — Bronze Layer (Ingestion)
# MAGIC
# MAGIC **Big Data Course — UPB**
# MAGIC
# MAGIC The Bronze layer stores data **raw, exactly as it arrives** from the sources.
# MAGIC
# MAGIC - Sources can be any format: CSV, JSON, XML, JDBC, APIs...
# MAGIC - Data is **read** in its original format and **written** to Delta Lake
# MAGIC - The **content** is not transformed — only the **storage format** changes
# MAGIC - This gives us ACID, time travel, and schema evolution on raw data
# MAGIC
# MAGIC Dataset: Uber Movement — Travel Times (7 cities, CSV format)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuration — Azure Data Lake Storage Gen2
# MAGIC
# MAGIC ### Prerequisites
# MAGIC 1. Create a Storage Account with **hierarchical namespace enabled** (ADLS Gen2)
# MAGIC 2. Create a container named `bigdata`
# MAGIC 3. Upload the 7 Uber Travel Times CSVs to the path:
# MAGIC    ```
# MAGIC    bigdata/
# MAGIC    └── landing/
# MAGIC        └── uber/
# MAGIC            ├── Travel_Times - Bogota.csv
# MAGIC            ├── Travel_Times - Boston.csv
# MAGIC            ├── Travel_Times - Johannesburg and Pretoria.csv
# MAGIC            ├── Travel_Times - Manila.csv
# MAGIC            ├── Travel_Times - Paris.csv
# MAGIC            ├── Travel_Times - Sydney.csv
# MAGIC            └── Travel_Times - Washington DC.csv
# MAGIC    ```
# MAGIC 4. Configure access from Databricks (see next cell)

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit, input_file_name
from pyspark.sql.types import *

# ─── CONFIGURE THESE VARIABLES ────────────────────────────────────────────────
# Replace with your Storage Account values
STORAGE_ACCOUNT = "<your_storage_account>"   # e.g.: "introbigdataupb"
CONTAINER       = "bigdata"
ACCESS_KEY      = "<your_access_key>"        # get from Azure Portal → Storage Account → Access Keys
# ──────────────────────────────────────────────────────────────────────────────

# Configure access to ADLS Gen2 via Access Key
spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    ACCESS_KEY
)

# ──────────────────────────────────────────────────────────────────────────────
# NOTE: In production, NEVER put the key directly in the notebook.
# Use Databricks Secrets:
#   1. Create scope:  databricks secrets create-scope --scope adls-scope
#   2. Store key:     databricks secrets put-secret --scope adls-scope --key storage-key
#   3. In the notebook:
#      ACCESS_KEY = dbutils.secrets.get(scope="adls-scope", key="storage-key")
# ──────────────────────────────────────────────────────────────────────────────

# ADLS Gen2 paths (abfss:// protocol)
ADLS_BASE    = f"abfss://{CONTAINER}@{STORAGE_ACCOUNT}.dfs.core.windows.net"
RAW_PATH     = f"{ADLS_BASE}/landing/uber/"
BRONZE_PATH  = f"{ADLS_BASE}/medallion/bronze/travel_times"
BRONZE_TABLE = "medallion.bronze_travel_times"

print(f"✅ ADLS Gen2 configured")
print(f"   Landing zone: {RAW_PATH}")
print(f"   Bronze path:  {BRONZE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Read raw data (multiple CSVs)
# MAGIC
# MAGIC ### Why do we read CSV but write Delta?
# MAGIC
# MAGIC Data sources arrive in any format: CSV, JSON, XML, JDBC, APIs, etc.
# MAGIC In Bronze **we don't transform the content** — the data stays as-is.
# MAGIC What we do is change the **storage format** to Delta to gain:
# MAGIC - ACID transactions (if the write fails, automatic rollback)
# MAGIC - Time travel (query previous versions)
# MAGIC - Schema evolution (add columns without breaking anything)
# MAGIC
# MAGIC ### Why read everything as STRING?
# MAGIC
# MAGIC If a field that should be a number contains text (e.g.: "N/A", "null", "---"),
# MAGIC an automatic cast would convert it to NULL and **we'd lose the original data**.
# MAGIC In Bronze we read everything as STRING to preserve 100% of the data.
# MAGIC Type validation and casting is the **Silver** layer's job, not Bronze's.

# COMMAND ----------

# Raw schema — we read EVERYTHING as STRING to avoid data loss
# Why? If "Mean Travel Time" has a value like "N/A" in some record,
# a cast to Double would convert it to NULL and we'd lose the original data.
# Type validation is Silver's job, not Bronze's.
raw_schema = StructType([
    StructField("Origin Movement ID", StringType()),
    StructField("Origin Display Name", StringType()),
    StructField("Origin Geometry", StringType()),
    StructField("Destination Movement ID", StringType()),
    StructField("Destination Display Name", StringType()),
    StructField("Destination Geometry", StringType()),
    StructField("Date Range", StringType()),
    StructField("Mean Travel Time (Seconds)", StringType()),
    StructField("Range - Lower Bound Travel Time (Seconds)", StringType()),
    StructField("Range - Upper Bound Travel Time (Seconds)", StringType()),
])

# Read CSVs in their original format
# spark.read.csv → reads CSV | spark.read.json → reads JSON | spark.read.jdbc → reads DB
# In Bronze, the source can be any format. The key is NOT to transform the content.
df_raw = (spark.read
    .option("header", "true")
    .schema(raw_schema)          # STRING schema to preserve everything
    .csv(RAW_PATH + "*.csv")     # ← source is CSV here, but could be .json, .parquet, etc.
)

# Add ingestion metadata (Bronze pattern)
# These fields allow tracking WHEN and WHERE each record came from
df_bronze = (df_raw
    .withColumn("_ingestion_timestamp", current_timestamp())  # when it was ingested
    .withColumn("_source_file", input_file_name())            # which file it came from
)

print(f"✅ Raw records read: {df_bronze.count()}")
df_bronze.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Write to Bronze (CSV → Delta)
# MAGIC
# MAGIC This is where the format conversion happens: data that arrived as CSV
# MAGIC is written as **Delta Lake**. The content is identical — only the
# MAGIC storage format changes to gain ACID, time travel, and schema evolution.

# COMMAND ----------

# Write as Delta — append mode (we never overwrite Bronze)
# Data that arrived as CSV is now stored as Delta
# Content: IDENTICAL to the original CSV | Format: Delta (Parquet + transaction log)
(df_bronze.write
    .format("delta")             # ← STORAGE format: Delta
    .mode("append")              # ← append-only: we never overwrite Bronze
    .option("mergeSchema", "true")  # ← allows adding new columns in future ingestions
    .save(BRONZE_PATH)
)

print(f"✅ Data written to Bronze: {BRONZE_PATH}")

# COMMAND ----------

# Register as a table for SQL queries
spark.sql(f"CREATE DATABASE IF NOT EXISTS medallion")
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {BRONZE_TABLE}
USING DELTA
LOCATION '{BRONZE_PATH}'
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Verify Bronze

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM medallion.bronze_travel_times LIMIT 5

# COMMAND ----------

# MAGIC %sql
# MAGIC -- How many records per source file?
# MAGIC SELECT _source_file, COUNT(*) as records
# MAGIC FROM medallion.bronze_travel_times
# MAGIC GROUP BY _source_file

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Version history (Time Travel)
# MAGIC
# MAGIC Delta Lake keeps a log of every operation. We can view the history
# MAGIC and query previous versions.

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY medallion.bronze_travel_times

# COMMAND ----------

# MAGIC %md
# MAGIC ## Key takeaways for Bronze
# MAGIC
# MAGIC - ✅ Sources can be any format (CSV, JSON, XML, JDBC, APIs)
# MAGIC - ✅ Data is READ in its original format, WRITTEN to Delta
# MAGIC - ✅ Content is NOT transformed — only the storage format changes
# MAGIC - ✅ All types as STRING (we don't lose data due to type errors)
# MAGIC - ✅ Ingestion metadata: `_ingestion_timestamp`, `_source_file`
# MAGIC - ✅ Append-only — we never delete or overwrite
# MAGIC - ✅ Delta format → ACID, time travel, schema evolution
# MAGIC - ✅ Historical source of truth — if something fails, we reprocess from here
