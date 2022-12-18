"""This creates recommendations for a group based on what manga they have
translated."""

"""Generate metadata that maps groups/manga/chapters to their respective ids.

This is useful for traversing the relationships between the different metadata
"""
from argparse import ArgumentParser
from pathlib import Path

from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import IndexToString, StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.sql import functions as F

from manga_recsys.commands.utils import write_df, write_df_per_group
from manga_recsys.spark import get_spark


def parse_args():
    """Parse the input path, output path, and spark options."""
    parser = ArgumentParser()
    parser.add_argument("input_chapter", help="Input path for chapter metadata")
    parser.add_argument("input_group_manga", help="Input path for group manga metadata")
    parser.add_argument("output", help="Output path")
    parser.add_argument("--num_recs", type=int, default=20)
    parser.add_argument("--cores", type=int, default=16)
    parser.add_argument("--memory", default="24g")
    return parser.parse_args()


def main():
    args = parse_args()
    spark = get_spark(cores=args.cores, memory=args.memory)

    chapter = spark.read.parquet(args.input_chapter)
    group_manga = spark.read.parquet(args.input_group_manga)

    # create a pipeline that string vectorizes both scanlation_group and manga, then fits an ALS model
    pipeline = Pipeline(
        stages=[
            StringIndexer(
                inputCol="scanlation_group", outputCol="scanlation_group_idx"
            ),
            StringIndexer(inputCol="manga", outputCol="manga_idx"),
            ALS(
                userCol="scanlation_group_idx",
                itemCol="manga_idx",
                ratingCol="pages",
                nonnegative=True,
                coldStartStrategy="drop",
            ),
        ]
    )

    scan_manga = (
        chapter.select("attributes.pages", "relationships.*")
        .groupby("manga", "scanlation_group")
        .agg(F.sum("pages").alias("pages"))
        .orderBy(F.desc("pages"))
        .where("manga is not null and scanlation_group is not null")
    )
    model = pipeline.fit(scan_manga)
    scan_manga_pred = model.transform(scan_manga)

    # evaluate with RMSE
    evaluator = RegressionEvaluator(
        metricName="rmse", labelCol="pages", predictionCol="prediction"
    )
    rmse = evaluator.evaluate(scan_manga_pred)
    print(f"Root-mean-square error = {rmse}")

    user_recs = model.stages[-1].recommendForAllUsers(args.num_recs)

    exploded_user_recs = user_recs.withColumn(
        "exploded", F.explode("recommendations")
    ).select("scanlation_group_idx", "exploded.*")

    inverse_pipeline = Pipeline(
        stages=[
            IndexToString(
                inputCol="scanlation_group_idx",
                outputCol="scanlation_group",
                labels=model.stages[0].labels,
            ),
            IndexToString(
                inputCol="manga_idx", outputCol="manga", labels=model.stages[1].labels
            ),
        ]
    )

    inversed_recs = (
        inverse_pipeline.fit(exploded_user_recs)
        .transform(exploded_user_recs)
        .select(
            F.col("scanlation_group").alias("group_id"),
            F.col("manga").alias("manga_id"),
            F.col("rating"),
        )
        .join(
            group_manga.select("group_id", "group_name").distinct(),
            on="group_id",
        )
        .join(
            group_manga.select("manga_id", "manga_name").distinct(),
            on="manga_id",
        )
    )
    inversed_recs.printSchema()
    inversed_recs.show()

    # now write this out to parquet
    write_df(inversed_recs, Path(args.output) / "recommendations.parquet")
    write_df_per_group(inversed_recs, Path(args.output) / "recommendations")


if __name__ == "__main__":
    main()
