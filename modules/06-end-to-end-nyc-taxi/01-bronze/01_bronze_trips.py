# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze: ingesta de viajes desde el landing compartido
# MAGIC
# MAGIC Lee los Parquet mensuales del landing y los persiste como Delta
# MAGIC en el Volume del estudiante. Opera en modo **append** mes a mes,
# MAGIC permitiendo cargas incrementales.
# MAGIC
# MAGIC **Idempotencia**: si un mes ya fue ingestado, se salta automáticamente.
# MAGIC
# MAGIC ## Uso
# MAGIC
# MAGIC Ajusta `MONTHS_TO_INGEST` para controlar qué meses se cargan.

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Parámetros de ingesta

# COMMAND ----------

# Meses a ingerir en esta ejecución.
# Ajusta según lo que necesites cargar.
MONTHS_TO_INGEST = [
    (2023, 1), (2023, 2), (2023, 3),
    (2023, 4), (2023, 5), (2023, 6),
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Ingesta incremental (append)
# MAGIC
# MAGIC Cada mes se lee con `read_yellow_trips_month`, que detecta
# MAGIC automáticamente la variante de esquema (v1/v2/v3) y devuelve
# MAGIC un DataFrame con el `UNIFIED_SCHEMA`.
# MAGIC
# MAGIC Antes de escribir, se verifica si el mes ya fue ingestado
# MAGIC consultando `_source_file` en la tabla Delta bronze.

# COMMAND ----------

def _already_ingested(spark, year: int, month: int) -> bool:
    """Verifica si un mes ya fue ingestado en bronze."""
    import os
    month_str = f"{year}-{month:02d}"
    pattern = f"%yellow_tripdata_{month_str}%"

    # Si el directorio Delta no existe aún, no hay nada ingestado
    if not os.path.exists(PATH_BRONZE_TRIPS + "_delta_log"):
        try:
            spark.read.format("delta").load(PATH_BRONZE_TRIPS)
        except Exception:
            return False

    try:
        count = (
            spark.read.format("delta").load(PATH_BRONZE_TRIPS)
            .filter(F.col("_source_file").like(pattern))
            .limit(1)
            .count()
        )
        return count > 0
    except Exception:
        return False

# COMMAND ----------

for year, month in MONTHS_TO_INGEST:
    print(f"\n{'─'*60}")
    print(f"  {year}-{month:02d}", end="")

    if _already_ingested(spark, year, month):
        print(f" → ⏭️  ya ingestado, saltando")
        continue

    print(f" → ingiriendo...")
    print(f"{'─'*60}")

    df = (
        read_yellow_trips_month(spark, year, month)
        .withColumn("_ingested_at", F.current_timestamp())
    )

    (
        df.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .save(PATH_BRONZE_TRIPS)
    )

    print(f"  ✓ Append completado para {year}-{month:02d}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Verificación

# COMMAND ----------

bronze = spark.read.format("delta").load(PATH_BRONZE_TRIPS)

bronze.agg(
    F.count("*").alias("total_rows"),
    F.min("tpep_pickup_datetime").alias("min_pickup"),
    F.max("tpep_pickup_datetime").alias("max_pickup"),
    F.countDistinct(
        F.year("tpep_pickup_datetime"),
        F.month("tpep_pickup_datetime")
    ).alias("distinct_months"),
).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Historial Delta
# MAGIC
# MAGIC Cada append queda registrado como una transacción independiente.
# MAGIC Esto permite time travel y auditoría de qué meses se cargaron.

# COMMAND ----------

from delta.tables import DeltaTable

dt = DeltaTable.forPath(spark, PATH_BRONZE_TRIPS)
display(dt.history())
