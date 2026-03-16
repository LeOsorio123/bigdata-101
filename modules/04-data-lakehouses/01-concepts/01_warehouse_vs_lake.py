# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Data Warehouse vs Data Lake vs Lakehouse
# MAGIC
# MAGIC **Big Data Course — UPB**
# MAGIC
# MAGIC In this notebook we explore the fundamental differences between the three
# MAGIC data architectures, using practical examples in Databricks.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Simulating a Data Warehouse (Schema-on-Write)
# MAGIC
# MAGIC In a warehouse, the schema is defined **before** loading the data.
# MAGIC If the data doesn't match the schema, it gets rejected.

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# We define the schema BEFORE loading (Schema-on-Write)
warehouse_schema = StructType([
    StructField("origin_id", IntegerType(), False),
    StructField("origin_name", StringType(), False),
    StructField("destination_id", IntegerType(), False),
    StructField("destination_name", StringType(), False),
    StructField("mean_travel_time_sec", DoubleType(), False),
    StructField("lower_bound_sec", DoubleType(), True),
    StructField("upper_bound_sec", DoubleType(), True),
])

print("✅ Schema defined. In a warehouse, data MUST comply with this.")
warehouse_schema

# COMMAND ----------

# MAGIC %md
# MAGIC ### Problem: data that doesn't match the schema
# MAGIC
# MAGIC What happens when data arrives with extra columns, incorrect types, or null fields?

# COMMAND ----------

from pyspark.sql import Row

# "Good" data — matches the schema
good_data = [
    Row(origin_id=183, origin_name="SANTA INES", destination_id=4,
        destination_name="PALO BLANCO", mean_travel_time_sec=2296.0,
        lower_bound_sec=1639.0, upper_bound_sec=3215.0),
]

# "Bad" data — has an extra field and an incorrect type
bad_data_raw = [
    {"origin_id": "NOT_A_NUMBER", "origin_name": "TEST",
     "destination_id": 1, "destination_name": "DEST",
     "mean_travel_time_sec": 100.0, "extra_field": "surprise"}
]

df_good = spark.createDataFrame(good_data, schema=warehouse_schema)
df_good.show()

# This would fail in a real warehouse:
print("⚠️  In a warehouse, data with incorrect types or extra columns is REJECTED")
print("   This is Schema-on-Write: the schema is validated AT WRITE TIME")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Simulating a Data Lake (Schema-on-Read)
# MAGIC
# MAGIC In a lake, we store data **as-is** and apply
# MAGIC the schema when we read it. We use Azure Data Lake Storage Gen2.

# COMMAND ----------

# ─── CONFIGURE THESE VARIABLES ────────────────────────────────────────────────
STORAGE_ACCOUNT = "<your_storage_account>"   # e.g.: "introbigdataupb"
CONTAINER       = "bigdata"
ACCESS_KEY      = "<your_access_key>"
# In production use: ACCESS_KEY = dbutils.secrets.get(scope="adls-scope", key="storage-key")
# ──────────────────────────────────────────────────────────────────────────────

spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    ACCESS_KEY
)

ADLS_BASE = f"abfss://{CONTAINER}@{STORAGE_ACCOUNT}.dfs.core.windows.net"
RAW_PATH  = f"{ADLS_BASE}/landing/uber/"

# Read a CSV without schema — Schema-on-Read
df_lake = (spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(RAW_PATH + "Travel_Times - Bogota.csv")
)

print("✅ Data Lake: data is stored as-is, without validation")
print("   The schema is inferred AT READ TIME (Schema-on-Read)")
print(f"   Inferred columns: {df_lake.columns}")
df_lake.printSchema()
print("   ⚠️  Problem: are the types correct? Are there duplicates? Are there nulls?")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Data Lakehouse: the best of both worlds
# MAGIC
# MAGIC With Delta Lake, we get Schema-on-Write **on top of** lake-style storage.

# COMMAND ----------

# Create a Delta table with enforced schema
spark.sql("DROP TABLE IF EXISTS demo_lakehouse.travel_times")
spark.sql("""
CREATE TABLE IF NOT EXISTS demo_lakehouse.travel_times (
    origin_id INT NOT NULL,
    origin_name STRING NOT NULL,
    destination_id INT NOT NULL,
    destination_name STRING NOT NULL,
    mean_travel_time_sec DOUBLE NOT NULL,
    lower_bound_sec DOUBLE,
    upper_bound_sec DOUBLE
)
USING DELTA
COMMENT 'Lakehouse table with schema enforcement on Delta Lake'
""")

print("✅ Lakehouse: Delta table with enforced schema")
print("   - Cheap storage (like a lake)")
print("   - Schema enforcement (like a warehouse)")
print("   - ACID transactions, time travel, schema evolution")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary comparison
# MAGIC
# MAGIC | Feature | Warehouse | Lake | Lakehouse |
# MAGIC |---|---|---|---|
# MAGIC | Schema | Schema-on-Write | Schema-on-Read | Schema-on-Write (flexible) |
# MAGIC | ACID | ✅ | ❌ | ✅ |
# MAGIC | Formats | Proprietary | Open (Parquet) | Open (Delta/Iceberg) |
# MAGIC | Cost | High | Low | Low |
# MAGIC | SQL | ✅ | Limited | ✅ |
# MAGIC | ML/DS | Difficult | ✅ | ✅ |
