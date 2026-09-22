"""Spark SQL demonstration layer for CricAnalyser.

Run after the cleaned Parquet datasets exist:
    spark-submit spark/spark_sql_queries.py
"""
from pathlib import Path
from pyspark.sql import SparkSession

BASE=Path(__file__).resolve().parents[1]
CLEAN=BASE/"data/cleaned"

spark=(SparkSession.builder.appName("CricAnalyser-SparkSQL").getOrCreate())
matches=spark.read.parquet(str(CLEAN/"matches"))
deliveries=spark.read.parquet(str(CLEAN/"deliveries"))

matches.createOrReplaceTempView("matches")
deliveries.createOrReplaceTempView("deliveries")

queries={
"season_totals": """
SELECT season, COUNT(DISTINCT match_id) AS matches,
       SUM(total_runs) AS runs, SUM(is_wicket) AS wickets
FROM deliveries GROUP BY season ORDER BY season
""",
"top_batters": """
SELECT batter, SUM(batsman_runs) AS runs,
       COUNT(DISTINCT match_id) AS matches
FROM deliveries GROUP BY batter
ORDER BY runs DESC LIMIT 20
""",
"top_bowlers": """
SELECT bowler, SUM(is_wicket) AS wickets,
       SUM(total_runs) AS runs_conceded,
       COUNT(DISTINCT STRUCT(match_id, inning, over)) AS overs_recorded
FROM deliveries GROUP BY bowler
ORDER BY wickets DESC, runs_conceded ASC LIMIT 20
""",
"venue_scoring": """
SELECT m.venue, m.city, COUNT(DISTINCT d.match_id) AS matches,
       SUM(d.total_runs) AS runs
FROM deliveries d JOIN matches m ON d.match_id=m.match_id
GROUP BY m.venue, m.city ORDER BY runs DESC
"""
}

for name,sql in queries.items():
    print(f"\n=== {name} ===")
    spark.sql(sql).show(20, truncate=False)

spark.stop()
