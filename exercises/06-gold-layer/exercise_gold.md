# Ejercicio: Capa Gold — Agregaciones de negocio

## Objetivo

Construir **3 tablas Gold** a partir de la capa Silver (trips limpios y enriquecidos) que consoliden métricas de negocio listas para consumo en dashboards y análisis.

## Contexto

Ya tienes disponible la tabla Silver en `PATH_SILVER_TRIPS` con los viajes limpios, enriquecidos con:
- Información de zonas: `pickup_borough`, `pickup_zone`, `dropoff_borough`, `dropoff_zone`
- Features temporales: `pickup_date`, `pickup_hour`, `pickup_dayofweek`, `is_weekend`, `is_rush_hour`
- Features económicas: `tip_rate`, `cost_per_mile`, `avg_speed_mph`
- Columnas base: `trip_distance`, `trip_duration_min`, `fare_amount`, `tip_amount`, `total_amount`, `passenger_count`, `PULocationID`, `DOLocationID`

Tu notebook debe comenzar con:
```python
%run ../00-setup/config

from pyspark.sql import functions as F
from pyspark.sql import Window

enriched = spark.read.format("delta").load(PATH_SILVER_TRIPS)
```

---

## Tabla 1: Revenue por zona

**Objetivo:** Crear una tabla agregada por zona de pickup para alimentar un heatmap geográfico de ingresos.

### Requisitos

- Filtrar registros donde `pickup_zone` no sea nulo
- Agrupar por: `pickup_borough`, `pickup_zone`, `PULocationID`
- Calcular las siguientes métricas:
  | Columna | Descripción |
  |---------|-------------|
  | `total_trips` | Cantidad total de viajes |
  | `total_revenue` | Suma de `total_amount` (redondeado a 2 decimales) |
  | `avg_fare` | Promedio de `total_amount` (redondeado a 2 decimales) |
  | `total_tips` | Suma de `tip_amount` (redondeado a 2 decimales) |
  | `avg_tip_pct` | Promedio de `tip_rate` × 100 (redondeado a 2 decimales) |
  | `avg_distance_mi` | Promedio de `trip_distance` (redondeado a 2 decimales) |
  | `avg_duration_min` | Promedio de `trip_duration_min` (redondeado a 2 decimales) |

- Escribir en Delta con `mode("overwrite")` en un path Gold (ej: `PATH_GOLD_REVENUE_BY_ZONE`)

### Verificación

Muestra las top 20 zonas por `total_revenue` descendente. ¿Cuál es la zona con más ingresos?

---

## Tabla 2: Métricas diarias

**Objetivo:** Crear una serie temporal diaria para dashboards de monitoreo operativo.

### Requisitos

- Agrupar por: `pickup_date`
- Calcular las siguientes métricas:
  | Columna | Descripción |
  |---------|-------------|
  | `total_trips` | Cantidad de viajes del día |
  | `total_revenue` | Suma de `total_amount` |
  | `avg_fare` | Promedio de `total_amount` |
  | `avg_distance_mi` | Promedio de `trip_distance` |
  | `avg_duration_min` | Promedio de `trip_duration_min` |
  | `avg_speed_mph` | Promedio de `avg_speed_mph` |
  | `total_tips` | Suma de `tip_amount` |
  | `avg_tip_pct` | Promedio de `tip_rate` × 100 |
  | `unique_pickup_zones` | Cantidad de zonas de pickup distintas (`countDistinct`) |

- Ordenar por `pickup_date`
- Escribir en Delta con `mode("overwrite")`

### Bonus: Detección de anomalías

Después de escribir la tabla, implementa una detección simple de días anómalos:

1. Calcula la media y desviación estándar de `total_trips` sobre toda la tabla
2. Calcula el z-score para cada día: `(total_trips - media) / desviación`
3. Filtra los días con `|z_score| > 2`
4. Muestra esos días ordenados por z-score

**Pregunta:** ¿Qué días tienen demanda anormalmente baja o alta? ¿Puedes explicar por qué? (festivos, clima, eventos...)

---

## Tabla 3: Demanda por hora y zona

**Objetivo:** Crear una tabla de demanda granular para análisis de patrones temporales (heatmaps hora × zona).

### Requisitos

Para esta tabla, usa **SQL puro** con `spark.sql()`:

- Crear la tabla con `CREATE OR REPLACE TABLE`
- Filtrar donde `pickup_zone IS NOT NULL`
- Agrupar por: `pickup_borough`, `pickup_zone`, `pickup_hour`, `pickup_dayofweek`, `is_weekend`, `is_rush_hour`
- Calcular:
  | Columna | Descripción |
  |---------|-------------|
  | `trips` | `COUNT(*)` |
  | `avg_fare` | `ROUND(AVG(total_amount), 2)` |
  | `avg_speed_mph` | `ROUND(AVG(avg_speed_mph), 2)` |

- Después de crear la tabla, ejecutar:
  ```sql
  OPTIMIZE <tabla> ZORDER BY (pickup_zone, pickup_hour)
  ```

### Verificación

Ejecuta un query que muestre las top 10 combinaciones zona-hora con más viajes durante rush hour (`is_rush_hour = true`).

**Pregunta:** ¿Por qué usamos `ZORDER BY (pickup_zone, pickup_hour)`? ¿Qué tipo de queries se benefician?

---

## Entregables

1. Un notebook `.py` (formato Databricks) con las 3 tablas Gold
2. Cada sección debe tener:
   - Un encabezado `%md` explicando qué hace
   - El código de transformación
   - Una celda de verificación/display
3. Responder las preguntas planteadas en celdas `%md`

## Pistas

- Usa `F.round()` para redondear métricas
- `F.countDistinct("col")` cuenta valores únicos
- Para SQL, las tablas Silver deben estar registradas en el catálogo o usar una vista temporal:
  ```python
  enriched.createOrReplaceTempView("silver_trips")
  spark.sql("SELECT ... FROM silver_trips ...")
  ```
- `ZORDER` reorganiza los datos físicamente para acelerar queries con filtros sobre esas columnas
- El z-score mide cuántas desviaciones estándar se aleja un valor de la media

## Criterios de evaluación

| Criterio | Peso |
|----------|------|
| Tabla revenue_by_zone correcta y completa | 25% |
| Tabla daily_metrics correcta y completa | 25% |
| Detección de anomalías (bonus) | 15% |
| Tabla hourly_demand en SQL con ZORDER | 25% |
| Respuestas a preguntas y documentación | 10% |
