$ErrorActionPreference = "Stop"
hdfs dfs -mkdir -p /ipl/raw
hdfs dfs -mkdir -p /ipl/cleaned
hdfs dfs -mkdir -p /ipl/processed
hdfs dfs -ls /ipl
Write-Host "CricAnalyser HDFS directories created."
