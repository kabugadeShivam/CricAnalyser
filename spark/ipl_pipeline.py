"""End-to-end Spark analytics for CricAnalyser.

Run locally:
    spark-submit spark/ipl_pipeline.py

The job reads cleaned Parquet data and writes Power BI-ready CSV datasets.
"""

from pathlib import Path
from pyspark.sql import SparkSession, functions as F, Window

BASE = Path(__file__).resolve().parents[1]
CLEAN = BASE / "data" / "cleaned"
OUT = BASE / "data" / "processed"


def spark_session():
    return (
        SparkSession.builder
        .appName("CricAnalyser-IPL-Analytics")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def write_csv(df, name):
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    (
        df.coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(str(target))
    )


def main():
    spark = spark_session()
    OUT.mkdir(parents=True, exist_ok=True)

    matches = spark.read.parquet(str(CLEAN / "matches")).cache()
    deliveries = spark.read.parquet(str(CLEAN / "deliveries")).cache()

    # One delivery can contain runs off the bat and extras.
    batting = (
        deliveries.groupBy("batter")
        .agg(
            F.sum("batsman_runs").alias("runs"),
            F.sum(F.when(F.col("batsman_runs") == 4, 1).otherwise(0)).alias("fours"),
            F.sum(F.when(F.col("batsman_runs") == 6, 1).otherwise(0)).alias("sixes"),
            F.countDistinct("match_id").alias("matches_played")
        )
        .withColumn(
            "runs_per_match",
            F.round(F.col("runs") / F.col("matches_played"), 2)
        )
        .orderBy(F.desc("runs"))
    )

    # Approximate batting innings: distinct match + inning + batting team + batter.
    innings = (
        deliveries.groupBy("match_id", "inning", "batting_team", "batter")
        .agg(
            F.sum("batsman_runs").alias("runs"),
            F.sum(F.when(F.col("batsman_runs") == 4, 1).otherwise(0)).alias("fours"),
            F.sum(F.when(F.col("batsman_runs") == 6, 1).otherwise(0)).alias("sixes"),
            F.max("is_wicket").alias("dismissed")
        )
    )
    consistency = (
        innings.groupBy("batter")
        .agg(
            F.count("*").alias("innings"),
            F.round(F.avg("runs"), 2).alias("avg_runs"),
            F.round(F.stddev("runs"), 2).alias("run_stddev"),
            F.sum(F.when(F.col("runs") >= 30, 1).otherwise(0)).alias("30_plus"),
            F.sum(F.when(F.col("runs") >= 50, 1).otherwise(0)).alias("50_plus"),
            F.sum(F.when(F.col("runs") >= 100, 1).otherwise(0)).alias("100_plus")
        )
        .withColumn(
            "consistency_score",
            F.round(
                F.when(F.col("run_stddev").isNull(), F.col("avg_runs"))
                .otherwise(F.col("avg_runs") / (F.col("run_stddev") + F.lit(1))),
                2
            )
        )
        .orderBy(F.desc("consistency_score"))
    )

    bowling = (
        deliveries.groupBy("bowler")
        .agg(
            F.sum("total_runs").alias("runs_conceded"),
            F.sum("is_wicket").alias("wickets"),
            F.countDistinct(
                F.struct("match_id", "inning", "over")
            ).alias("overs_recorded"),
            F.countDistinct("match_id").alias("matches_bowled")
        )
        .withColumn(
            "economy",
            F.round(F.col("runs_conceded") / F.col("overs_recorded"), 2)
        )
        .orderBy(F.desc("wickets"), F.asc("economy"))
    )

    # Phase: over 0-5 = powerplay, 6-14 = middle, 15+ = death.
    phase = (
        deliveries
        .withColumn(
            "phase",
            F.when(F.col("over") < 6, "Powerplay")
             .when(F.col("over") < 15, "Middle")
             .otherwise("Death")
        )
        .groupBy("season", "phase")
        .agg(
            F.sum("total_runs").alias("runs"),
            F.count("*").alias("deliveries"),
            F.sum("is_wicket").alias("wickets")
        )
        .withColumn("run_rate", F.round(F.col("runs") / (F.col("deliveries") / 6.0), 2))
        .orderBy("season", "phase")
    )

    team = (
        deliveries.groupBy("season", "batting_team")
        .agg(
            F.sum("total_runs").alias("runs_scored"),
            F.sum("batsman_runs").alias("bat_runs"),
            F.sum("is_wicket").alias("wickets_lost"),
            F.countDistinct("match_id").alias("matches")
        )
        .withColumn("runs_per_match", F.round(F.col("runs_scored") / F.col("matches"), 2))
        .orderBy("season", F.desc("runs_scored"))
    )

    venue = (
        deliveries.join(
            matches.select("match_id", "venue", "city"),
            "match_id",
            "inner"
        )
        .groupBy("venue", "city")
        .agg(
            F.countDistinct("match_id").alias("matches"),
            F.sum("total_runs").alias("runs"),
            F.round(F.avg("total_runs"), 2).alias("avg_runs_per_delivery"),
            F.sum("is_wicket").alias("wickets")
        )
        .orderBy(F.desc("runs"))
    )

    toss = (
        matches.withColumn(
            "toss_result",
            F.when(F.col("toss_winner") == F.col("winner"), "Toss winner won")
             .otherwise("Toss winner lost")
        )
        .groupBy("season", "toss_decision", "toss_result")
        .agg(F.count("*").alias("matches"))
        .orderBy("season", "toss_decision", "toss_result")
    )

    match_summary = (
        matches.withColumn(
            "win_margin",
            F.when(F.col("win_by_runs") > 0,
                   F.concat(F.col("win_by_runs"), F.lit(" runs")))
             .when(F.col("win_by_wickets") > 0,
                   F.concat(F.col("win_by_wickets"), F.lit(" wickets")))
             .otherwise(F.coalesce(F.col("result"), F.lit("normal")))
        )
        .select(
            "match_id","season","date","venue","city","team1","team2",
            "toss_winner","toss_decision","winner","win_by_runs",
            "win_by_wickets","player_of_match","win_margin"
        )
    )

    # Season overview joins match and ball-level totals.
    season_runs = (
        deliveries.groupBy("season")
        .agg(
            F.sum("total_runs").alias("total_runs"),
            F.sum("is_wicket").alias("total_wickets"),
            F.countDistinct("match_id").alias("matches")
        )
        .withColumn("runs_per_match", F.round(F.col("total_runs") / F.col("matches"), 2))
        .orderBy("season")
    )

    outputs = {
        "batting": batting,
        "batting_consistency": consistency,
        "bowling": bowling,
        "phase_analysis": phase,
        "team_season": team,
        "venue_analysis": venue,
        "toss_analysis": toss,
        "match_summary": match_summary,
        "season_overview": season_runs,
    }

    for name, df in outputs.items():
        print(f"Writing {name}: {df.count():,} rows")
        write_csv(df, name)

    spark.stop()


if __name__ == "__main__":
    main()
