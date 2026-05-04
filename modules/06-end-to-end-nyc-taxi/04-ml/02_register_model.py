# Databricks notebook source
# MAGIC %md
# MAGIC # Registro del modelo en Unity Catalog

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Widget para el `run_id`
# MAGIC
# MAGIC Corre esta celda primero para crear el widget. Luego pega en el
# MAGIC widget (arriba del notebook) el `run_id` que imprimió el notebook
# MAGIC `01_train_trip_duration`.

# COMMAND ----------

dbutils.widgets.text("run_id", "", "Run ID del training")

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

import mlflow
from mlflow.tracking import MlflowClient

spark.sql(f"USE CATALOG {CATALOG}")
mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Crear el schema ML si no existe (para el modelo)

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA_ML}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Leer el `run_id` del widget

# COMMAND ----------

run_id = dbutils.widgets.get("run_id").strip()

assert run_id, "Pega el run_id del notebook 01_train_trip_duration en el widget 'run_id'."
print(f"Registrando modelo del run: {run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Registrar en UC

# COMMAND ----------

model_uri = f"runs:/{run_id}/model"
registered = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)
print(f"✓ Registrado {MODEL_NAME} versión {registered.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Asignar alias `challenger`

# COMMAND ----------

client = MlflowClient()
client.set_registered_model_alias(name=MODEL_NAME, alias="challenger", version=registered.version)
print(f"✓ Alias 'challenger' asignado a versión {registered.version}")
