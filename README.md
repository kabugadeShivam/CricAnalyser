# CricAnalyser

## Big Data Analytics for IPL Match and Player Performance Using Hadoop and Apache Spark

A college Big Data Analytics project that processes IPL match-level and ball-by-ball data using Hadoop HDFS, Apache Spark/PySpark and Spark SQL, with Power BI for interactive visualization.

### Pipeline

IPL data → Data Cleaning → HDFS → Apache Spark → PySpark/Spark SQL → Analytical datasets → Power BI

### Planned analysis

- Season-wise scoring
- Batting performance
- Bowling performance
- Team performance
- Venue analysis
- Toss and match outcomes
- Chasing vs defending
- Powerplay, middle-over and death-over analysis
- Boundary analysis
- Player consistency

### Dataset

The project uses separate match-level and delivery-level datasets:

- `matches.csv`
- `deliveries.csv`

The current educational dataset covers IPL-style records from 2008–2025. It should be described transparently as an educational/synthetic dataset unless independently verified against an authoritative historical source.

### Project structure

```
CricAnalyser/
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
├── hadoop/
├── spark/
├── src/
│   ├── data_cleaning/
│   ├── batting/
│   ├── bowling/
│   ├── teams/
│   └── venues/
├── notebooks/
├── dashboard/
├── screenshots/
├── report/
└── README.md
```

## Status

Step 1 — Project definition and dataset selection: complete.

Step 2 — Local setup, dataset validation and HDFS ingestion: next.
