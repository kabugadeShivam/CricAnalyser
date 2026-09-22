"""Optional ML extension: first-innings final-score prediction.

This module is deliberately separate from the Big Data core. It aggregates the
ball-by-ball data into match snapshots and trains a simple Random Forest model.
"""
from pathlib import Path
from pyspark.sql import SparkSession, functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

BASE=Path(__file__).resolve().parents[2]
CLEAN=BASE/"data/cleaned"

spark=SparkSession.builder.appName("CricAnalyser-ML").getOrCreate()
d=spark.read.parquet(str(CLEAN/"deliveries"))
m=spark.read.parquet(str(CLEAN/"matches")).select("match_id","venue","season")

# Build snapshots at the end of each first-innings over. Target = final innings score.
first=d.filter(F.col("inning")==1)
final_scores=(first.groupBy("match_id").agg(F.sum("total_runs").alias("final_score")))
snapshots=(first.groupBy("match_id","season","over")
    .agg(F.sum("total_runs").alias("score"),F.sum("is_wicket").alias("wickets"))
    .join(final_scores,"match_id")
    .join(m,"match_id")
    .filter(F.col("over").isin(5,9,14))
    .withColumn("overs_completed",F.col("over")+F.lit(1)))

venue_index=StringIndexer(inputCol="venue",outputCol="venue_index",handleInvalid="keep")
assembler=VectorAssembler(
    inputCols=["season","over","score","wickets","overs_completed","venue_index"],
    outputCol="features")
model=RandomForestRegressor(featuresCol="features",labelCol="final_score",numTrees=50,maxDepth=8,seed=42)
pipeline=Pipeline(stages=[venue_index,assembler,model])

train,test=snapshots.randomSplit([0.8,0.2],seed=42)
fitted=pipeline.fit(train)
pred=fitted.transform(test)

rmse=RegressionEvaluator(labelCol="final_score",predictionCol="prediction",metricName="rmse").evaluate(pred)
mae=RegressionEvaluator(labelCol="final_score",predictionCol="prediction",metricName="mae").evaluate(pred)
print(f"Test RMSE: {rmse:.2f}")
print(f"Test MAE: {mae:.2f}")
pred.select("match_id","season","overs_completed","score","wickets","final_score","prediction").show(20,truncate=False)
spark.stop()
