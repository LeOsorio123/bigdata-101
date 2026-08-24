# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Data Warehouse vs Data Lake vs Lakehouse
# MAGIC
# MAGIC **Big Data Course — UPB**
# MAGIC
# MAGIC In this notebook we explore the fundamental differences between the three
# MAGIC data architectures, using practical examples in Databricks.
# MAGIC
# MAGIC **What you will learn:**
# MAGIC 1. How Schema-on-Write works (Warehouse) — and what happens when data doesn't comply
# MAGIC 2. How Schema-on-Read works (Lake) — and the problems it introduces
# MAGIC 3. How a Lakehouse combines both — with live demonstrations of schema enforcement,
# MAGIC    ACID transactions, and time travel

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Configuration
# MAGIC
# MAGIC Each student uses their own schema (last name) within the shared catalog.
# MAGIC Update the variable `SCHEMA` with your last name.

# COMMAND ----------

# ─── CONFIGURE YOUR LAST NAME HERE ───────────────────────────────────────────
CATALOG = "maestria_bd_2026_01"
SCHEMA  = None  # <-- Change to your last name (lowercase, e.g. "garcia")
VOLUME  = "datalake"
# ──────────────────────────────────────────────────────────────────────────────

assert SCHEMA is not None, "⚠️ You must set SCHEMA to your last name before continuing!"

# Unity Catalog volume path (accessible in serverless)
VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

print(f"Catalog: {CATALOG}")
print(f"Schema:  {SCHEMA}")
print(f"Volume:  {VOLUME_PATH}")

# Set default catalog and schema for SQL commands
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 1. Data Warehouse — Schema-on-Write
# MAGIC
# MAGIC In a warehouse, the schema is defined **before** loading the data.
# MAGIC If the data doesn't match the schema, it gets **rejected**.
# MAGIC
# MAGIC Key characteristics:
# MAGIC - Strict types and constraints
# MAGIC - Data is validated at write time
# MAGIC - No "dirty" data enters the system

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1.1 Define a strict schema

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# We define the schema BEFORE loading (Schema-on-Write)
warehouse_schema = StructType([
    StructField("origin_id", IntegerType(), False),       # NOT NULL
    StructField("origin_name", StringType(), False),      # NOT NULL
    StructField("destination_id", IntegerType(), False),  # NOT NULL
    StructField("destination_name", StringType(), False), # NOT NULL
    StructField("mean_travel_time_sec", DoubleType(), False),  # NOT NULL
    StructField("lower_bound_sec", DoubleType(), True),   # nullable
    StructField("upper_bound_sec", DoubleType(), True),   # nullable
])

print("✅ Schema defined. In a warehouse, data MUST comply with this structure.")
print(f"   Columns: {len(warehouse_schema.fields)}")
print(f"   Required (NOT NULL): {sum(1 for f in warehouse_schema.fields if not f.nullable)}")
warehouse_schema

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1.2 Insert valid data — success

# COMMAND ----------

from pyspark.sql import Row

# Data that matches the schema perfectly
good_data = [
    Row(origin_id=183, origin_name="SANTA INES", destination_id=4,
        destination_name="PALO BLANCO", mean_travel_time_sec=2296.0,
        lower_bound_sec=1639.0, upper_bound_sec=3215.0),
    Row(origin_id=45, origin_name="CHAPINERO", destination_id=12,
        destination_name="USAQUEN", mean_travel_time_sec=1450.0,
        lower_bound_sec=980.0, upper_bound_sec=2100.0),
]

df_good = spark.createDataFrame(good_data, schema=warehouse_schema)
print("✅ Valid data — accepted by the warehouse schema:")
df_good.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1.3 Insert invalid data — rejection
# MAGIC
# MAGIC What happens when data has wrong types, extra columns, or missing required fields?

# COMMAND ----------

# Attempt 1: wrong type in origin_id (string instead of int)
print("─── Attempt 1: Wrong data type ───")
try:
    bad_rows = [Row(origin_id="NOT_A_NUMBER", origin_name="TEST",
                    destination_id=1, destination_name="DEST",
                    mean_travel_time_sec=100.0,
                    lower_bound_sec=None, upper_bound_sec=None)]
    df_bad = spark.createDataFrame(bad_rows, schema=warehouse_schema)
    df_bad.show()
except Exception as e:
    print(f"❌ REJECTED: {type(e).__name__}")
    print(f"   {str(e)[:200]}")

# COMMAND ----------

# Attempt 2: missing required field (origin_name is None)
print("─── Attempt 2: NULL in a NOT NULL field ───")
try:
    bad_rows_null = [Row(origin_id=99, origin_name=None,
                         destination_id=1, destination_name="DEST",
                         mean_travel_time_sec=100.0,
                         lower_bound_sec=None, upper_bound_sec=None)]
    df_bad_null = spark.createDataFrame(bad_rows_null, schema=warehouse_schema)
    df_bad_null.show()
    print("⚠️  Note: PySpark DataFrames don't enforce NOT NULL at creation time.")
    print("   The constraint is enforced when writing to a Delta table (see Section 3).")
except Exception as e:
    print(f"❌ REJECTED: {type(e).__name__}")
    print(f"   {str(e)[:200]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🔑 Warehouse takeaway
# MAGIC
# MAGIC - Schema is defined **before** data arrives
# MAGIC - Invalid data is **rejected** at write time
# MAGIC - Guarantees data quality but is **rigid** — schema changes are expensive

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 2. Data Lake — Schema-on-Read
# MAGIC
# MAGIC In a lake, we store data **as-is** (raw files) and apply
# MAGIC the schema only when we read it.
# MAGIC
# MAGIC We use a **Unity Catalog Volume** as our lake storage layer.
# MAGIC
# MAGIC Key characteristics:
# MAGIC - Any format, any structure
# MAGIC - Cheap storage (object store)
# MAGIC - Schema is inferred or applied at read time
# MAGIC - No guarantees about data quality

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.1 Explore raw files in the lake

# COMMAND ----------

# Path to the raw CSV files in the volume
RAW_PATH = f"{VOLUME_PATH}/landing/uber/"

# List files available in the volume
print(f"📂 Files in: {RAW_PATH}\n")
files = dbutils.fs.ls(RAW_PATH)
for f in files:
    print(f"   {f.name} ({f.size:,} bytes)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.2 Read without schema — Schema-on-Read

# COMMAND ----------

# Read a CSV without defining a schema — the engine infers it
df_lake = (spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{RAW_PATH}Travel_Times - Bogota.csv")
)

print("📖 Data Lake: Schema-on-Read")
print(f"   Rows: {df_lake.count()}")
print(f"   Columns: {df_lake.columns}\n")
df_lake.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.3 The problems with Schema-on-Read

# COMMAND ----------

from pyspark.sql.functions import col, count, when, isnan

# Problem 1: Are there nulls?
print("─── Problem 1: NULL values ───")
null_counts = df_lake.select([
    count(when(col(c).isNull(), c)).alias(c) for c in df_lake.columns
])
null_counts.show(truncate=False)

# COMMAND ----------

# Problem 2: Are the types correct? Let's read the SAME file with all strings
df_lake_strings = (spark.read
    .option("header", "true")
    .option("inferSchema", "false")  # everything as string
    .csv(f"{RAW_PATH}Travel_Times - Bogota.csv")
)

print("─── Problem 2: Type ambiguity ───")
print("With inferSchema=true:")
print(f"   mean_travel_time: {df_lake.schema['Mean Travel Time (Seconds)'].dataType}")
print("\nWith inferSchema=false (all strings):")
print(f"   mean_travel_time: {df_lake_strings.schema['Mean Travel Time (Seconds)'].dataType}")
print("\n⚠️  Same data, different schemas depending on how you read it!")

# COMMAND ----------

# Problem 3: No protection against duplicates
print("─── Problem 3: No duplicate protection ───")
total_rows = df_lake.count()
distinct_rows = df_lake.distinct().count()
print(f"   Total rows:    {total_rows}")
print(f"   Distinct rows: {distinct_rows}")
print(f"   Duplicates:    {total_rows - distinct_rows}")
print("\n⚠️  A lake has no mechanism to prevent or detect duplicates at write time.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🔑 Data Lake takeaway
# MAGIC
# MAGIC - Data is stored **as-is** — no validation
# MAGIC - Schema is applied **at read time** — different readers can interpret data differently
# MAGIC - Cheap and flexible, but **no quality guarantees**
# MAGIC - Problems: nulls, type mismatches, duplicates, no ACID transactions

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 3. Data Lakehouse — Best of Both Worlds
# MAGIC
# MAGIC With **Delta Lake**, we get:
# MAGIC - Schema enforcement (like a warehouse)
# MAGIC - Cheap open storage (like a lake)
# MAGIC - ACID transactions
# MAGIC - Time travel (query previous versions)
# MAGIC - Schema evolution (add columns without breaking)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.1 Create a Delta table with enforced schema

# COMMAND ----------

# Create a Delta table with strict schema
spark.sql("DROP TABLE IF EXISTS travel_times")
spark.sql("""
CREATE TABLE travel_times (
    origin_id INT NOT NULL,
    origin_name STRING NOT NULL,
    destination_id INT NOT NULL,
    destination_name STRING NOT NULL,
    mean_travel_time_sec DOUBLE NOT NULL,
    lower_bound_sec DOUBLE,
    upper_bound_sec DOUBLE
)
USING DELTA
COMMENT 'Lakehouse table — schema enforcement + open storage + ACID'
""")

print(f"✅ Delta table created: {CATALOG}.{SCHEMA}.travel_times")
spark.sql("DESCRIBE TABLE travel_times").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.2 Insert valid data — success

# COMMAND ----------

# Insert valid data into the Delta table
df_good.write.mode("append").saveAsTable("travel_times")

print("✅ Valid data inserted successfully:")
spark.sql("SELECT * FROM travel_times").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.3 Insert invalid data — schema enforcement in action

# COMMAND ----------

# Attempt: insert data with a NULL in a NOT NULL column
print("─── Attempt: NULL in a NOT NULL column ───")
try:
    bad_df = spark.createDataFrame(
        [(99, None, 1, "DEST", 100.0, None, None)],
        schema=["origin_id", "origin_name", "destination_id",
                "destination_name", "mean_travel_time_sec",
                "lower_bound_sec", "upper_bound_sec"]
    )
    bad_df.write.mode("append").saveAsTable("travel_times")
    print("Inserted (unexpected)")
except Exception as e:
    print(f"❌ REJECTED by Delta: {type(e).__name__}")
    print(f"   {str(e)[:300]}")
    print("\n✅ Schema enforcement works! The lakehouse protects data quality.")

# COMMAND ----------

# Attempt: insert data with an extra column (schema mismatch)
print("─── Attempt: Extra column not in schema ───")
try:
    extra_col_df = spark.createDataFrame(
        [(10, "A", 20, "B", 500.0, None, None, "EXTRA_VALUE")],
        schema=["origin_id", "origin_name", "destination_id",
                "destination_name", "mean_travel_time_sec",
                "lower_bound_sec", "upper_bound_sec", "extra_column"]
    )
    extra_col_df.write.mode("append").saveAsTable("travel_times")
    print("Inserted (unexpected)")
except Exception as e:
    print(f"❌ REJECTED by Delta: {type(e).__name__}")
    print(f"   {str(e)[:300]}")
    print("\n✅ Extra columns are rejected — schema is enforced at write time.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.4 ACID Transactions — consistency guaranteed

# COMMAND ----------

# Show that the table still only has the valid data
print("After failed inserts, the table remains consistent (ACID):")
spark.sql("SELECT COUNT(*) as total_rows FROM travel_times").show()
spark.sql("SELECT * FROM travel_times").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.5 Time Travel — query previous versions

# COMMAND ----------

# Insert more data to create a new version
more_data = [
    Row(origin_id=7, origin_name="KENNEDY", destination_id=22,
        destination_name="SUBA", mean_travel_time_sec=1800.0,
        lower_bound_sec=1200.0, upper_bound_sec=2500.0),
]
df_more = spark.createDataFrame(more_data, schema=warehouse_schema)
df_more.write.mode("append").saveAsTable("travel_times")

print("✅ New data inserted. Let's compare versions:\n")

# Current version
print("── Current version (latest): ──")
spark.sql("SELECT * FROM travel_times").show(truncate=False)

# Previous version (before the last insert)
print("── Previous version (VERSION 1): ──")
spark.sql("SELECT * FROM travel_times VERSION AS OF 1").show(truncate=False)

# COMMAND ----------

# View the history of changes
print("── Table history (all versions): ──")
spark.sql("DESCRIBE HISTORY travel_times").select(
    "version", "timestamp", "operation", "operationMetrics"
).show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.6 Schema Evolution — add columns without breaking existing data

# COMMAND ----------

# Enable schema evolution and add a new column
spark.sql("ALTER TABLE travel_times ADD COLUMNS (city STRING)")

print("✅ Column 'city' added via schema evolution.")
print("   Existing rows get NULL for the new column:\n")
spark.sql("SELECT * FROM travel_times").show(truncate=False)

# COMMAND ----------

# Insert data with the new column
spark.sql("""
INSERT INTO travel_times VALUES
    (50, 'TEUSAQUILLO', 30, 'FONTIBON', 2100.0, 1500.0, 2800.0, 'Bogota')
""")

print("✅ New row with 'city' populated:")
spark.sql("SELECT * FROM travel_times").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 🔑 Lakehouse takeaway
# MAGIC
# MAGIC - **Schema enforcement** at write time (like a warehouse)
# MAGIC - **Open format** storage on cheap object stores (like a lake)
# MAGIC - **ACID transactions** — failed writes don't corrupt data
# MAGIC - **Time travel** — query any previous version
# MAGIC - **Schema evolution** — add columns without rewriting data

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 4. Summary Comparison
# MAGIC
# MAGIC | Feature | Warehouse | Lake | Lakehouse |
# MAGIC |---|---|---|---|
# MAGIC | Schema | Schema-on-Write | Schema-on-Read | Schema-on-Write (flexible) |
# MAGIC | ACID | ✅ | ❌ | ✅ |
# MAGIC | Formats | Proprietary | Open (CSV, Parquet, JSON) | Open (Delta/Iceberg) |
# MAGIC | Cost | High | Low | Low |
# MAGIC | SQL | ✅ | Limited | ✅ |
# MAGIC | ML/DS | Difficult | ✅ | ✅ |
# MAGIC | Time Travel | Limited | ❌ | ✅ |
# MAGIC | Schema Evolution | Expensive | N/A | ✅ (cheap) |
# MAGIC | Data Quality | High | Low | High |

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 5. Cleanup (optional)
# MAGIC
# MAGIC Uncomment the following cell to drop the table created in this notebook.

# COMMAND ----------

# spark.sql("DROP TABLE IF EXISTS travel_times")
# print("🧹 Table dropped.")
