# CricAnalyser

## Big Data Analytics for IPL Match and Player Performance Using Hadoop and Apache Spark

CricAnalyser is an end-to-end college **Big Data Analytics** project using **Hadoop HDFS, Apache Spark/PySpark, Spark SQL, Power BI** and a modern **Next.js analytics dashboard**.

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
          HDFS
            |
            v
       PySpark Cleaning
            |
            v
      Parquet datasets
            |
            v
      Spark Analytics
            |
            v
      Processed outputs
        /           \
       v             v
   Power BI      Next.js Dashboard
```

HDFS and Spark form the Big Data processing layer. The web dashboard consumes the same processed analytical schema. For cloud demonstration, a small committed demo snapshot is used because normal web hosting does not run the local Hadoop/Spark stack.

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

The development dataset contains approximately **1,044 matches and 251,951 delivery records**, spanning **2008–2025**. It is treated as an **IPL-style educational/synthetic dataset** unless independently verified against official historical records.

## Repository structure

```
CricAnalyser/
├── app/                    # Next.js dashboard + analytics API
├── config/                 # project configuration
├── data/
│   ├── raw/                # local input CSVs; ignored by Git
│   ├── cleaned/            # generated Parquet
│   ├── processed/          # local Spark outputs; ignored by Git
│   └── demo/processed/     # small deployable demonstration snapshot
├── hadoop/                 # HDFS setup/upload scripts
├── spark/                  # Spark analytics + Spark SQL + HDFS job
├── src/                    # validation, cleaning and optional ML
├── dashboard/              # Power BI guide
├── docs/                   # report, data dictionary and deployment guide
├── tests/                  # project tests
├── .github/workflows/      # automated Next.js build check
├── run_pipeline.ps1
├── requirements.txt
└── package.json
```

## Windows setup

### 1. Clone

```powershell
git clone https://github.com/kabugadeShivam/CricAnalyser.git
cd CricAnalyser
```

### 2. Python environment

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

### 4. Validate

```powershell
python src\\data_cleaning\\validate_raw.py
```

### 5. Clean with PySpark

```powershell
python src\\data_cleaning\\clean_data.py
```

Creates:

```
data/cleaned/matches/
data/cleaned/deliveries/
```

Both are **Parquet** datasets.

### 6. Run analytics

```powershell
spark-submit spark\\ipl_pipeline.py
```

Outputs:

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

Expected layout:

```
/ipl/raw
/ipl/cleaned
/ipl/processed
```

### 9. Spark SQL

```powershell
spark-submit spark\\spark_sql_queries.py
```

### 10. Run the web dashboard

```powershell
npm install
npm run build
npm run dev
```

Open `http://localhost:3000`.

The dashboard contains:

1. **Overview**
2. **Batting**
3. **Bowling**
4. **Teams**
5. **Venues**
6. **Insights**

The API first looks for local Spark output and otherwise uses the committed demonstration snapshot.

### 11. Power BI

Follow [dashboard/POWER_BI_GUIDE.md](dashboard/POWER_BI_GUIDE.md).

### 12. Optional ML

```powershell
spark-submit src\\ml\\score_predictor.py
```

## Cloud deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

The Next.js application is structured for **Vercel deployment**. No environment variables are required for the dashboard demo. The cloud version uses the committed demo snapshot while the full Hadoop/Spark pipeline remains reproducible locally.

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

## Demonstration status

- [x] Big Data architecture
- [x] Dataset schema and validation
- [x] PySpark cleaning
- [x] Spark analytics
- [x] Spark SQL
- [x] HDFS scripts
- [x] Power BI design
- [x] Optional ML extension
- [x] Modern Next.js dashboard
- [x] Dashboard API
- [x] Deployable demo analytics snapshot
- [x] Deployment guide
- [x] Automated Next.js build workflow

**Ready for demonstration and deployment.**

> Data note: the dataset is treated as IPL-style educational/synthetic data. Do not present generated values as verified official IPL statistics.
