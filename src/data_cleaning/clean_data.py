"""Clean and validate the IPL match and ball-by-ball datasets with PySpark."""

from pathlib import Path
from pyspark.sql import SparkSession, functions as F, types as T

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw"
CLEAN = BASE / "data" / "cleaned"

MATCH_COLUMNS = [
    "match_id","season","date","venue","city","team1","team2",
    "toss_winner","toss_decision","winner","result","win_by_runs",
    "win_by_wickets","player_of_match"
]

DELIVERY_COLUMNS = [
    "match_id","season","inning","over","ball","batting_team","bowling_team",
    "batter","bowler","batsman_runs","extra_runs","total_runs","extra_type",
    "is_wicket","player_dismissed","dismissal_type"
]


def spark_session():
    return (
        SparkSession.builder
        .appName("CricAnalyser-Cleaning")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def require_columns(df, columns, name):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing columns: {missing}")


def clean_matches(spark):
    path = str(RAW / "matches.csv")
    df = spark.read.option("header", True).option("inferSchema", True).csv(path)
    require_columns(df, MATCH_COLUMNS, "matches.csv")

    out = (
        df.select(*MATCH_COLUMNS)
        .withColumn("match_id", F.col("match_id").cast("string"))
        .withColumn("season", F.col("season").cast("int"))
        .withColumn("date", F.to_date("date"))
        .withColumn("win_by_runs", F.coalesce(F.col("win_by_runs").cast("int"), F.lit(0)))
        .withColumn("win_by_wickets", F.coalesce(F.col("win_by_wickets").cast("int"), F.lit(0)))
        .dropDuplicates(["match_id"])
        .filter(F.col("match_id").isNotNull())
        .filter(F.col("season").between(2008, 2100))
        .na.fill({
            "result": "normal",
            "city": "Unknown",
            "venue": "Unknown",
            "toss_decision": "unknown"
        })
    )
    return out


def clean_deliveries(spark, valid_match_ids):
    path = str(RAW / "deliveries.csv")
    df = spark.read.option("header", True).option("inferSchema", True).csv(path)
    require_columns(df, DELIVERY_COLUMNS, "deliveries.csv")

    out = (
        df.select(*DELIVERY_COLUMNS)
        .withColumn("match_id", F.col("match_id").cast("string"))
        .withColumn("season", F.col("season").cast("int"))
        .withColumn("inning", F.col("inning").cast("int"))
        .withColumn("over", F.col("over").cast("int"))
        .withColumn("ball", F.col("ball").cast("int"))
        .withColumn("batsman_runs", F.col("batsman_runs").cast("int"))
        .withColumn("extra_runs", F.col("extra_runs").cast("int"))
        .withColumn("total_runs", F.col("total_runs").cast("int"))
        .withColumn("is_wicket", F.col("is_wicket").cast("int"))
        .dropDuplicates()
        .filter(F.col("match_id").isNotNull())
        .filter(F.col("match_id").isin(valid_match_ids))
        .filter(F.col("inning").isin(1, 2))
        .filter(F.col("over").between(0, 50))
        .filter(F.col("batsman_runs") >= 0)
        .filter(F.col("extra_runs") >= 0)
        .filter(F.col("total_runs") >= 0)
        .filter(F.col("is_wicket").isin(0, 1))
        .withColumn(
            "total_runs",
            F.when(
                F.col("total_runs") != F.col("batsman_runs") + F.col("extra_runs"),
                F.col("batsman_runs") + F.col("extra_runs")
            ).otherwise(F.col("total_runs"))
        )
    )
    return out


def main():
    spark = spark_session()
    CLEAN.mkdir(parents=True, exist_ok=True)

    matches = clean_matches(spark).cache()
    valid_ids = [r["match_id"] for r in matches.select("match_id").collect()]
    deliveries = clean_deliveries(spark, valid_ids).cache()

    matches.write.mode("overwrite").parquet(str(CLEAN / "matches"))
    deliveries.write.mode("overwrite").parquet(str(CLEAN / "deliveries"))

    print(f"Clean matches: {matches.count():,}")
    print(f"Clean deliveries: {deliveries.count():,}")
    print(f"Output: {CLEAN}")

    spark.stop()


if __name__ == "__main__":
    main()
