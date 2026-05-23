-- Serie temporal diaria: trips y revenue
-- Requiere vista temporal: spark.read.format("delta").load(PATH_GOLD_DAILY_METRICS).createOrReplaceTempView("daily_metrics")
SELECT
  pickup_date,
  total_trips,
  total_revenue,
  avg_fare
FROM daily_metrics
WHERE pickup_date BETWEEN :start_date AND :end_date
ORDER BY pickup_date;
