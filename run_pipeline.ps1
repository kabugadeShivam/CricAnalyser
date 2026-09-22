$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
python src\data_cleaning\validate_raw.py
if ($LASTEXITCODE -ne 0) { throw "Raw validation failed." }
python src\data_cleaning\clean_data.py
if ($LASTEXITCODE -ne 0) { throw "Spark cleaning failed." }
spark-submit spark\ipl_pipeline.py
if ($LASTEXITCODE -ne 0) { throw "Spark analytics failed." }
Write-Host "CricAnalyser pipeline completed."
