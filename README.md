# CricAnalyser

## Big Data Analytics for IPL Match and Player Performance Using Hadoop and Apache Spark

CricAnalyser is an end-to-end college **Big Data Analytics** project using **Hadoop HDFS, Apache Spark/PySpark, Spark SQL and Power BI**.

### Architecture

```
matches.csv + deliveries.csv
            |
            v
       data/raw/
            |
      Validation
            |
            v
       PySpark Cleaning
            |
            v
      data/cleaned/
       Parquet files
            |
            v
      Spark Analytics
            |
            v
      data/processed/
            |
            v
         Power BI
```

HDFS provides the distributed storage layer. The local Parquet/CSV path keeps development reproducible on Windows.

## Analytics implemented

- Season-wise scoring
- Top run scorers
- Boundary analysis
- Player consistency
- Top wicket takers
- Bowling economy
- Team season performance
- Powerplay / middle / death phases
- Venue analysis
- Toss analysis
- Match summaries
- Spark SQL demonstrations
- Optional first-innings score prediction with Spark MLlib

## Dataset

Two files are required in `data/raw/`:

### matches.csv
`match_id, season, date, venue, city, team1, team2, toss_winner, toss_decision, winner, result, win_by_runs, win_by_wickets, player_of_match`

### deliveries.csv
`match_id, season, inning, over, ball, batting_team, bowling_team, batter, bowler, batsman_runs, extra_runs, total_runs, extra_type, is_wicket, player_dismissed, dismissal_type`

The project dataset used during development contains approximately **1,044 matches and 251,951 delivery records**, spanning **2008–2025**. It is treated as an **IPL-style educational/synthetic dataset** unless independently verified against official historical IPL records.

## Repository structure

```
CricAnalyser/
├── config/
│   └── project_config.json
├── data/
│   ├── raw/                  # local input CSVs; ignored by Git
│   ├── cleaned/              # generated Parquet
│   └── processed/            # Power BI-ready outputs
├── hadoop/
│   ├── create_hdfs_dirs.ps1
│   └── upload_to_hdfs.ps1
├── spark/
│   ├── ipl_pipeline.py
│   └── spark_sql_queries.py
├── src/
│   ├── data_cleaning/
│   │   ├── validate_raw.py
│   │   └── clean_data.py
│   └── ml/
│       └── score_predictor.py
├── dashboard/
│   └── POWER_BI_GUIDE.md
├── docs/
│   ├── DATA_DICTIONARY.md
│   └── PROJECT_REPORT.md
├── tests/
│   └── test_project.py
├── run_pipeline.ps1
├── requirements.txt
└── README.md
```

## Windows setup

### 1. Clone

```powershell
git clone https://github.com/kabugadeShivam/CricAnalyser.git
cd CricAnalyser
```

### 2. Virtual environment

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Add data

Put the two files here:

```
data/raw/matches.csv
data/raw/deliveries.csv
```

The raw CSVs are intentionally excluded from Git because the ball-by-ball file is large.

### 4. Validate raw data

```powershell
python src\\data_cleaning\\validate_raw.py
```

### 5. Clean and transform with PySpark

```powershell
python src\\data_cleaning\\clean_data.py
```

This creates:

```
data/cleaned/matches/
data/cleaned/deliveries/
```

Both are **Parquet** datasets.

### 6. Run analytics

```powershell
spark-submit spark\\ipl_pipeline.py
```

Outputs are written under `data/processed/`:

- `batting`
- `batting_consistency`
- `bowling`
- `phase_analysis`
- `team_season`
- `venue_analysis`
- `toss_analysis`
- `match_summary`
- `season_overview`

### 7. One-command pipeline

After Spark is installed and available on PATH:

```powershell
.\\run_pipeline.ps1
```

### 8. Hadoop HDFS

After Hadoop is configured and NameNode/DataNode are running:

```powershell
.\\hadoop\\create_hdfs_dirs.ps1
.\\hadoop\\upload_to_hdfs.ps1
hdfs dfs -ls -h /ipl/raw
```

Expected HDFS layout:

```
/ipl/raw
/ipl/cleaned
/ipl/processed
```

### 9. Spark SQL

After cleaning:

```powershell
spark-submit spark\\spark_sql_queries.py
```

This demonstrates Spark SQL queries for season totals, top batters, top bowlers and venue scoring.

### 10. Power BI

Follow [dashboard/POWER_BI_GUIDE.md](dashboard/POWER_BI_GUIDE.md).

Recommended pages:

1. **IPL Overview**
2. **Batting Analysis**
3. **Bowling & Team Analysis**
4. **Match & Venue Analysis**

### 11. Optional ML

```powershell
spark-submit src\\ml\\score_predictor.py
```

The ML extension predicts first-innings final score from intermediate match state features. It is intentionally separate from the core Big Data pipeline.

## Data quality handling

The cleaning stage performs:

- column/schema validation
- type conversion
- duplicate removal
- missing-value defaults
- valid innings and over filtering
- non-negative run checks
- `match_id` relational filtering
- run consistency correction

## Project report

Use [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md) as the report structure and [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) for the dataset chapter.

## Status

- [x] Project architecture
- [x] Dataset schema
- [x] Validation
- [x] PySpark cleaning
- [x] Spark analytics
- [x] Spark SQL
- [x] HDFS scripts
- [x] Power BI design
- [x] Optional ML extension
- [ ] Run the full pipeline on the user's Windows machine
- [ ] Build and export the final Power BI dashboard
- [ ] Add screenshots and measured results to the report
