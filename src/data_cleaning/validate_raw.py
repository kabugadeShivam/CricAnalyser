"""Fast schema and quality validation for raw CSV files."""

from pathlib import Path
import csv

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw"

MATCHES = [
    "match_id","season","date","venue","city","team1","team2",
    "toss_winner","toss_decision","winner","result","win_by_runs",
    "win_by_wickets","player_of_match"
]
DELIVERIES = [
    "match_id","season","inning","over","ball","batting_team","bowling_team",
    "batter","bowler","batsman_runs","extra_runs","total_runs","extra_type",
    "is_wicket","player_dismissed","dismissal_type"
]


def validate(path, required):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = [c for c in required if c not in fields]
        rows = 0
        bad = 0
        for row in reader:
            rows += 1
            if any(row.get(c, "") == "" for c in required[:2]):
                bad += 1
    print(f"{path.name}: {rows:,} rows")
    print(f"Columns: {len(fields)}")
    print(f"Missing required columns: {missing}")
    print(f"Rows missing key IDs: {bad:,}")
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    validate(RAW / "matches.csv", MATCHES)
    validate(RAW / "deliveries.csv", DELIVERIES)
    print("Raw validation completed.")
