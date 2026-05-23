# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze: ingesta de viajes desde el landing compartido
# MAGIC
# MAGIC Lee los Parquet que el profesor depositó en el landing y los persiste
# MAGIC como Delta en el Volume del estudiante (acceso por path, sin tablas).

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Leer el landing

# COMMAND ----------

raw = (
    read_yellow_trips(spark)
    .withColumn("_ingested_at", F.current_timestamp())
)

print(f"Leyendo desde: {LANDING_TRIPS_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Escribir a Delta en el Volume

# COMMAND ----------

(
    raw.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(PATH_BRONZE_TRIPS)
)

print(f"✓ Bronze escrito en {PATH_BRONZE_TRIPS}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Verificación

# COMMAND ----------

bronze = spark.read.format("delta").load(PATH_BRONZE_TRIPS)

bronze.agg(
    F.count("*").alias("total_rows"),
    F.min("tpep_pickup_datetime").alias("min_pickup"),
    F.max("tpep_pickup_datetime").alias("max_pickup"),
).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Anatomía de la tabla Delta
# MAGIC
# MAGIC Lo que escribimos no es un Parquet normal — es una tabla Delta
# MAGIC con transaction log, time travel y ACID.

# COMMAND ----------

from delta.tables import DeltaTable

dt = DeltaTable.forPath(spark, PATH_BRONZE_TRIPS)
display(dt.history())
