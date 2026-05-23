-- Distribución del porcentaje de propina (bucketizado)
-- Requiere vista temporal: spark.read.format("delta").load(PATH_SILVER_TRIPS_ENRICHED).createOrReplaceTempView("trips_enriched")
SELECT
  CASE
    WHEN tip_rate = 0              THEN '0%'
    WHEN tip_rate < 0.10           THEN '< 10%'
    WHEN tip_rate < 0.15           THEN '10-15%'
    WHEN tip_rate < 0.20           THEN '15-20%'
    WHEN tip_rate < 0.25           THEN '20-25%'
    ELSE '25%+'
  END AS tip_bucket,
  COUNT(*) AS trips,
  ROUND(AVG(fare_amount), 2) AS avg_fare
FROM trips_enriched
WHERE payment_type = 1   -- Solo tarjeta (cash tips no se registran)
  AND pickup_date BETWEEN :start_date AND :end_date
GROUP BY tip_bucket
ORDER BY
  CASE tip_bucket
    WHEN '0%'      THEN 1 WHEN '< 10%'  THEN 2 WHEN '10-15%' THEN 3
    WHEN '15-20%'  THEN 4 WHEN '20-25%' THEN 5 ELSE 6
  END;
