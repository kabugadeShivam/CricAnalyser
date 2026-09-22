"""Run Spark directly on raw data stored in HDFS.

Usage:
    spark-submit spark/ipl_hdfs_job.py

This creates distributed Parquet outputs under /ipl/processed. The local
ipl_pipeline.py remains the Power BI export path.
"""
from pyspark.sql import SparkSession, functions as F

spark=(SparkSession.builder
       .appName("CricAnalyser-HDFS-Job")
       .config("spark.sql.shuffle.partitions","8")
       .getOrCreate())

matches=(spark.read.option("header",True).option("inferSchema",True)
         .csv("hdfs:///ipl/raw/matches.csv"))
deliveries=(spark.read.option("header",True).option("inferSchema",True)
            .csv("hdfs:///ipl/raw/deliveries.csv"))

matches=matches.dropDuplicates(["match_id"]).cache()
valid_ids=matches.select("match_id").distinct()

deliveries=(deliveries.join(valid_ids,"match_id","inner")
            .dropDuplicates()
            .filter(F.col("inning").isin(1,2))
            .filter(F.col("batsman_runs")>=0)
            .filter(F.col("extra_runs")>=0)
            .filter(F.col("total_runs")>=0)
            .withColumn("total_runs",
                F.col("batsman_runs")+F.col("extra_runs")))

matches.write.mode("overwrite").parquet("hdfs:///ipl/processed/matches")
deliveries.write.mode("overwrite").parquet("hdfs:///ipl/processed/deliveries")

season_summary=(deliveries.groupBy("season")
                .agg(F.countDistinct("match_id").alias("matches"),
                     F.sum("total_runs").alias("runs"),
                     F.sum("is_wicket").alias("wickets"))
                .orderBy("season"))

season_summary.write.mode("overwrite").option("header",True).csv("hdfs:///ipl/processed/season_summary")

print("HDFS Spark job completed.")
print("Outputs:")
print("  /ipl/processed/matches")
print("  /ipl/processed/deliveries")
print("  /ipl/processed/season_summary")
spark.stop()
