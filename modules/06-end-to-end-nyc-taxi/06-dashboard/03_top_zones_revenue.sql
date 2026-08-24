-- Top 20 zonas de pickup por revenue total
-- Requiere vista temporal: spark.read.format("delta").load(PATH_GOLD_REVENUE_BY_ZONE).createOrReplaceTempView("revenue_by_zone")
SELECT
  pickup_zone,
  pickup_borough,
  total_trips,
  total_revenue,
  avg_fare,
  avg_tip_pct
FROM revenue_by_zone
WHERE pickup_borough = COALESCE(:borough, pickup_borough)
ORDER BY total_revenue DESC
LIMIT 20;
