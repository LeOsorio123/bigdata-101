# Databricks notebook source
# MAGIC %md
# MAGIC # Entrenamiento: predicción de duración de viaje (Spark MLlib)
# MAGIC
# MAGIC Usa un pipeline de Spark MLlib con `GBTRegressor` para predecir
# MAGIC la duración de un viaje en minutos. El modelo se loguea en MLflow.

# COMMAND ----------

# MAGIC %run ../00-setup/config

# COMMAND ----------

import mlflow
import mlflow.spark
from mlflow.models.signature import infer_signature
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator

spark.sql(f"USE CATALOG {CATALOG}")
mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Cargar features y split temporal
# MAGIC
# MAGIC Para evitar **data leakage** entre entrenamiento e inferencia usamos
# MAGIC un split temporal de 3 ventanas:
# MAGIC
# MAGIC - **Train**: `pickup_date < max_date - 30 días` → el modelo aprende aquí.
# MAGIC - **Test**:  `max_date - 30 días ≤ pickup_date < max_date - 7 días` →
# MAGIC   se usa solo para calcular RMSE / MAE / R² durante el entrenamiento.
# MAGIC - **Hold-out (últimos 7 días)**: **no** se usan aquí. Se reservan para
# MAGIC   el notebook `03_batch_inference`, simulando "datos nuevos" que el
# MAGIC   modelo nunca vio ni en train ni en test.
# MAGIC
# MAGIC Esto hace que las métricas de producción (en `03`) sean una evaluación
# MAGIC honesta sobre datos no vistos.

# COMMAND ----------

features_df = spark.table(T_ML_FEATURES)

# Muestreo del 5 % para agilizar el entrenamiento en clase
sample = features_df.sample(fraction=0.05, seed=42)

# Split temporal con hold-out de 7 días reservado para inferencia
max_date = sample.agg(F.max("pickup_date")).first()[0]
train_cutoff    = F.date_sub(F.lit(max_date), 30)  # fin de train
test_cutoff     = F.date_sub(F.lit(max_date), 7)   # fin de test / inicio hold-out

train_df = sample.filter(F.col("pickup_date") < train_cutoff)
test_df  = sample.filter(
    (F.col("pickup_date") >= train_cutoff) & (F.col("pickup_date") < test_cutoff)
)

print(f"Train: {train_df.count():,} | Test: {test_df.count():,}")
print(f"(Los últimos 7 días quedan como hold-out para 03_batch_inference)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Definir el pipeline de Spark MLlib

# COMMAND ----------

TARGET = "target_duration_min"
CATEGORICAL = ["pickup_borough", "dropoff_borough"]
NUMERIC = [
    "PULocationID", "DOLocationID", "pickup_hour", "pickup_dayofweek",
    "is_weekend", "is_rush_hour", "passenger_count", "trip_distance", "RatecodeID",
]

# --- Etapa 1: StringIndexer para las columnas categóricas (string → índice) ---
indexers = [
    StringIndexer(inputCol=c, outputCol=f"{c}_idx", handleInvalid="keep")
    for c in CATEGORICAL
]

# --- Etapa 2: OneHotEncoder sobre los índices ---
ohe = OneHotEncoder(
    inputCols=[f"{c}_idx" for c in CATEGORICAL],
    outputCols=[f"{c}_ohe" for c in CATEGORICAL],
    handleInvalid="keep",
)

# --- Etapa 3: VectorAssembler → combinar todo en un vector "features" ---
assembler_inputs = [f"{c}_ohe" for c in CATEGORICAL] + NUMERIC
assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="features", handleInvalid="skip")

# --- Etapa 4: GBTRegressor ---
gbt = GBTRegressor(
    featuresCol="features",
    labelCol=TARGET,
    maxIter=100,
    maxDepth=5,
    stepSize=0.1,
    seed=42,
)

pipeline = Pipeline(stages=indexers + [ohe, assembler, gbt])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Entrenar y evaluar

# COMMAND ----------

with mlflow.start_run(run_name=f"{USER_INITIALS}_gbt_trip_duration") as run:

    model = pipeline.fit(train_df)
    predictions = model.transform(test_df)

    # Métricas
    evaluator_rmse = RegressionEvaluator(labelCol=TARGET, predictionCol="prediction", metricName="rmse")
    evaluator_mae  = RegressionEvaluator(labelCol=TARGET, predictionCol="prediction", metricName="mae")
    evaluator_r2   = RegressionEvaluator(labelCol=TARGET, predictionCol="prediction", metricName="r2")

    rmse = evaluator_rmse.evaluate(predictions)
    mae  = evaluator_mae.evaluate(predictions)
    r2   = evaluator_r2.evaluate(predictions)

    mlflow.log_metrics({"test_rmse": rmse, "test_mae": mae, "test_r2": r2})
    mlflow.log_params({
        "student": USER_INITIALS,
        "algorithm": "GBTRegressor",
        "maxIter": 100,
        "maxDepth": 5,
        "stepSize": 0.1,
    })

    # Inferir signature a partir de un sample de inputs/outputs
    # (Unity Catalog exige signature al registrar el modelo)
    input_cols = CATEGORICAL + NUMERIC
    sample_input = train_df.select(*input_cols).limit(5).toPandas()
    sample_output = predictions.select("prediction").limit(5).toPandas()
    signature = infer_signature(sample_input, sample_output)

    # Loguear el PipelineModel de Spark con signature
    mlflow.spark.log_model(
        model,
        artifact_path="model",
        signature=signature,
    )

    run_id = run.info.run_id
    print(f"Run: {run_id}")
    print(f"RMSE: {rmse:.3f} | MAE: {mae:.3f} | R²: {r2:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Run ID para registrar el modelo
# MAGIC
# MAGIC Copia el `run_id` de abajo y pégalo en el notebook `02_register_model`
# MAGIC en la variable `run_id`.

# COMMAND ----------

print("=" * 60)
print(f"RUN_ID: {run_id}")
print("=" * 60)
print("👉 Copia este run_id y pégalo en 02_register_model.py")
