-- KPIs globales para counters del dashboard
-- NOTA: Este query requiere que los datos estén cargados en el path
-- PATH_SILVER_TRIPS_ENRICHED. Para usarlo en un dashboard SQL,
-- primero crea una vista temporal desde el notebook:
--   spark.read.format("delta").load(PATH_SILVER_TRIPS_ENRICHED).createOrReplaceTempView("trips_enriched")
-- Luego ejecuta este query sobre la vista.

SELECT
  COUNT(*)                                AS total_trips,
  ROUND(SUM(total_amount) / 1e6, 2)       AS total_revenue_millions,
  ROUND(AVG(total_amount), 2)             AS avg_fare,
  ROUND(AVG(trip_distance), 2)            AS avg_distance_mi,
  ROUND(AVG(trip_duration_min), 2)        AS avg_duration_min,
  ROUND(SUM(tip_amount) / 1e6, 2)         AS total_tips_millions,
  ROUND(AVG(tip_rate) * 100, 1)           AS avg_tip_pct
FROM trips_enriched
WHERE pickup_date BETWEEN :start_date AND :end_date;
