# Databricks notebook source
# MAGIC %md
# MAGIC # Delta Lake — Features avanzados
# MAGIC
# MAGIC **Cátedra de Big Data — UPB**
# MAGIC
# MAGIC Exploramos las capacidades que hacen de Delta Lake la base del Lakehouse:
# MAGIC ACID, Time Travel, Schema Evolution, MERGE (upserts) y optimización.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup: crear tabla de ejemplo

# COMMAND ----------

from pyspark.sql.functions import col, lit, current_timestamp
from pyspark.sql.types import *
from delta.tables import DeltaTable

# ─── CONFIGURAR ESTAS VARIABLES ───────────────────────────────────────────────
STORAGE_ACCOUNT = "<tu_storage_account>"
CONTAINER       = "bigdata"
ACCESS_KEY      = "<tu_access_key>"
# En producción usar: ACCESS_KEY = dbutils.secrets.get(scope="adls-scope", key="storage-key")
# ──────────────────────────────────────────────────────────────────────────────

spark.conf.set(
    f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net",
    ACCESS_KEY
)

ADLS_BASE  = f"abfss://{CONTAINER}@{STORAGE_ACCOUNT}.dfs.core.windows.net"
DELTA_PATH = f"{ADLS_BASE}/delta_demo/travel_times"

# Crear datos iniciales
data_v1 = [
    (1, "Centro", 2, "Aeropuerto", 2400.0, "Bogota"),
    (1, "Centro", 3, "Norte", 1800.0, "Bogota"),
    (5, "Chapinero", 2, "Aeropuerto", 3100.0, "Bogota"),
    (10, "CBD", 20, "Airport", 1500.0, "Sydney"),
    (10, "CBD", 30, "Bondi", 900.0, "Sydney"),
]

schema = StructType([
    StructField("origin_id", IntegerType()),
    StructField("origin_name", StringType()),
    StructField("destination_id", IntegerType()),
    StructField("destination_name", StringType()),
    StructField("mean_travel_time_sec", DoubleType()),
    StructField("city", StringType()),
])

df = spark.createDataFrame(data_v1, schema)
df.write.format("delta").mode("overwrite").save(DELTA_PATH)

spark.sql(f"DROP TABLE IF EXISTS delta_demo")
spark.sql(f"CREATE TABLE delta_demo USING DELTA LOCATION '{DELTA_PATH}'")

print("✅ Tabla delta_demo creada con 5 registros")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM delta_demo ORDER BY city, origin_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Transacciones ACID
# MAGIC
# MAGIC Delta garantiza que las operaciones son atómicas.
# MAGIC Si algo falla a mitad de una escritura, se hace rollback automático.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Insertar nuevos registros (operación atómica)
# MAGIC INSERT INTO delta_demo VALUES
# MAGIC   (15, 'Usaquén', 2, 'Aeropuerto', 2800.0, 'Bogota'),
# MAGIC   (20, 'Suba', 2, 'Aeropuerto', 3500.0, 'Bogota');

# COMMAND ----------

# MAGIC %sql
# MAGIC -- UPDATE atómico
# MAGIC UPDATE delta_demo
# MAGIC SET mean_travel_time_sec = 2200.0
# MAGIC WHERE origin_name = 'Centro' AND destination_name = 'Aeropuerto';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- DELETE atómico
# MAGIC DELETE FROM delta_demo WHERE origin_name = 'Suba';

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM delta_demo ORDER BY city, origin_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Time Travel
# MAGIC
# MAGIC Delta guarda un log de cada operación. Podemos consultar
# MAGIC cualquier versión anterior de los datos.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Ver historial de operaciones
# MAGIC DESCRIBE HISTORY delta_demo

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consultar la versión original (antes de INSERT, UPDATE, DELETE)
# MAGIC SELECT * FROM delta_demo VERSION AS OF 0 ORDER BY city, origin_id

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Comparar: ¿qué cambió entre versión 0 y la actual?
# MAGIC SELECT 'v0' as version, COUNT(*) as rows FROM delta_demo VERSION AS OF 0
# MAGIC UNION ALL
# MAGIC SELECT 'current', COUNT(*) FROM delta_demo

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Schema Evolution
# MAGIC
# MAGIC Agregar columnas sin romper nada. Los datos existentes
# MAGIC obtienen NULL en la nueva columna.

# COMMAND ----------

# Agregar columna "travel_minutes" a los datos nuevos
new_data = [
    (25, "Kennedy", 2, "Aeropuerto", 4000.0, "Bogota", 66.7),
]

new_schema = schema.add(StructField("travel_minutes", DoubleType()))
df_new = spark.createDataFrame(new_data, new_schema)

# mergeSchema permite agregar la nueva columna automáticamente
(df_new.write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .save(DELTA_PATH)
)

print("✅ Columna 'travel_minutes' agregada via schema evolution")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Los registros viejos tienen NULL en travel_minutes
# MAGIC SELECT origin_name, destination_name, mean_travel_time_sec, travel_minutes
# MAGIC FROM delta_demo
# MAGIC ORDER BY city, origin_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. MERGE (Upserts)
# MAGIC
# MAGIC Actualizar registros existentes e insertar nuevos en una sola operación.
# MAGIC Fundamental para CDC (Change Data Capture).

# COMMAND ----------

# Datos actualizados: Centro→Aeropuerto cambió, y hay una ruta nueva
updates = [
    (1, "Centro", 2, "Aeropuerto", 2100.0, "Bogota", 35.0),   # UPDATE
    (30, "Fontibón", 2, "Aeropuerto", 1200.0, "Bogota", 20.0), # INSERT
]

df_updates = spark.createDataFrame(updates, new_schema)

# MERGE: si existe → update, si no → insert
delta_table = DeltaTable.forPath(spark, DELTA_PATH)

(delta_table.alias("target")
    .merge(
        df_updates.alias("source"),
        "target.origin_id = source.origin_id AND target.destination_id = source.destination_id AND target.city = source.city"
    )
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

print("✅ MERGE ejecutado: 1 update + 1 insert")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM delta_demo WHERE city = 'Bogota' ORDER BY origin_id

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. OPTIMIZE y Z-ORDER
# MAGIC
# MAGIC Compactar archivos pequeños y ordenar datos para consultas rápidas.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Compactar archivos pequeños en archivos más grandes
# MAGIC OPTIMIZE delta_demo

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Z-ORDER: co-localizar datos por city para consultas filtradas
# MAGIC OPTIMIZE delta_demo ZORDER BY (city)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen de features Delta Lake
# MAGIC
# MAGIC | Feature | Descripción | Comando |
# MAGIC |---|---|---|
# MAGIC | ACID | Operaciones atómicas | INSERT, UPDATE, DELETE |
# MAGIC | Time Travel | Consultar versiones anteriores | VERSION AS OF n |
# MAGIC | Schema Evolution | Agregar columnas sin romper | mergeSchema = true |
# MAGIC | MERGE | Upserts (update + insert) | MERGE INTO ... |
# MAGIC | OPTIMIZE | Compactar archivos | OPTIMIZE tabla |
# MAGIC | Z-ORDER | Ordenar para consultas | ZORDER BY (col) |
