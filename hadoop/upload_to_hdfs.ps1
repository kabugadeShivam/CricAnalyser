$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Matches = Join-Path $Root "data\raw\matches.csv"
$Deliveries = Join-Path $Root "data\raw\deliveries.csv"
if (!(Test-Path $Matches)) { throw "Missing data/raw/matches.csv" }
if (!(Test-Path $Deliveries)) { throw "Missing data/raw/deliveries.csv" }
hdfs dfs -mkdir -p /ipl/raw
hdfs dfs -put -f $Matches /ipl/raw/matches.csv
hdfs dfs -put -f $Deliveries /ipl/raw/deliveries.csv
hdfs dfs -ls -h /ipl/raw
Write-Host "Raw IPL data uploaded to HDFS."
