# Databricks notebook source
# MAGIC %md
# MAGIC # Setup: catálogo personal en Unity Catalog
# MAGIC
# MAGIC Crea el catálogo del estudiante con sus esquemas y un Volume
# MAGIC `datalake` donde se almacenarán las capas medallion como Delta.
# MAGIC
# MAGIC ## Antes de correr
# MAGIC Abrir `config.py` y poner tus iniciales en `USER_INITIALS`.

# COMMAND ----------

# MAGIC %run ./config

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Usar catálogo del estudiante

# COMMAND ----------

try:
    spark.sql(f"USE CATALOG {CATALOG}")
    print(f"✓ Catálogo activo: {CATALOG}")
except Exception as e:
    if "CATALOG_NOT_FOUND" in str(e):
        print(f"⚠ Catálogo {CATALOG} no encontrado. Intentando crearlo...")
        managed_location = f"{EXTERNAL_LOCATION}/{CATALOG}"
        spark.sql(f"""
            CREATE CATALOG IF NOT EXISTS {CATALOG}
              MANAGED LOCATION '{managed_location}'
              COMMENT 'Lakehouse NYC Taxi — estudiante {USER_INITIALS}'
        """)
        spark.sql(f"USE CATALOG {CATALOG}")
        print(f"✓ Catálogo creado y activo: {CATALOG}")
    else:
        raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Esquemas Medallion + ML

# COMMAND ----------

for schema, comment in [
    (SCHEMA_BRONZE, "Capa Bronze: datos crudos tal cual llegan"),
    (SCHEMA_SILVER, "Capa Silver: datos limpios y validados"),
    (SCHEMA_GOLD,   "Capa Gold: KPIs y agregaciones de negocio"),
    (SCHEMA_ML,     "Features, predicciones y modelos de ML"),
]:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema} COMMENT '{comment}'")
    print(f"  ✓ {CATALOG}.{schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Volume para datos medallion (Delta por path)

# COMMAND ----------

spark.sql(f"""
    CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA_BRONZE}.{VOLUME_NAME}
      COMMENT 'Volume para almacenar capas medallion como Delta (bronze/silver/gold/ml)'
""")
print(f"  ✓ Volume: {VOLUME_BASE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Volume para MLflow (clústeres Shared/Serverless)

# COMMAND ----------

spark.sql(f"""
    CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA_ML}.{ML_VOLUME_NAME}
      COMMENT 'Directorio temporal para MLflow Spark models'
""")
print(f"  ✓ Volume MLflow: {ML_VOLUME_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Verificación

# COMMAND ----------

display(spark.sql(f"SHOW SCHEMAS IN {CATALOG}"))
