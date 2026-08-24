-- Top 20 pares origen→destino más frecuentes
-- Requiere vista temporal: spark.read.format("delta").load(PATH_SILVER_TRIPS_ENRICHED).createOrReplaceTempView("trips_enriched")
SELECT
  pickup_zone,
  dropoff_zone,
  COUNT(*)                         AS trips,
  ROUND(AVG(trip_distance), 2)     AS avg_distance,
  ROUND(AVG(total_amount), 2)      AS avg_fare,
  ROUND(AVG(trip_duration_min), 2) AS avg_duration_min
FROM trips_enriched
WHERE pickup_zone IS NOT NULL AND dropoff_zone IS NOT NULL
  AND pickup_date BETWEEN :start_date AND :end_date
GROUP BY pickup_zone, dropoff_zone
ORDER BY trips DESC
LIMIT 20;
