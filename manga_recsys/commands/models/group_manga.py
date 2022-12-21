"""This creates recommendations for a group based on what manga they have
translated."""

"""Generate metadata that maps groups/manga/chapters to their respective ids.

This is useful for traversing the relationships between the different metadata
"""
from pathlib import Path

import click
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import IndexToString, StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.sql import functions as F

from manga_recsys.commands.utils import write_df, write_df_per_uid
from manga_recsys.spark import get_spark


@click.command()
@click.argument("input_chapter", type=click.Path(exists=True))
@click.argument("input_group_manga", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--num-recs", type=int, default=20)
@click.option("--cores", type=int, default=16)
@click.option("--memory", default="24g")
def group_manga(input_chapter, input_group_manga, output, num_recs, cores, memory):
    """Create a recommendation for a group based on what manga they have translated.

    This effectively forms a bi-partite graph between groups and manga, with the
    edge weights being the number of chapters translated. We use alternating
    least-squares to compute the non-negative matrix factorization, which allows
    us to find latent factors for groups and manga.

    This is our starting point for analysis, since it's easy to construct.
    However, I do have concerns about the number of groups that overlap on a
    series because of scanlation culture of not "sniping" projects.
    """
    spark = get_spark(cores=cores, memory=memory)

    chapter = spark.read.parquet(input_chapter)
    group_manga = spark.read.parquet(input_group_manga)

    # create a pipeline that string vectorizes both scanlation_group and manga,
    # then fits an ALS model
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
        # log transform pages to make it look normal
        .withColumn("pages", F.log(F.col("pages") + 1))
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

    user_recs = model.stages[-1].recommendForAllUsers(num_recs)

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
    output = Path(output)
    gz_output = Path("/".join([output.parts[0], "gz", *output.parts[1:]]))
    write_df(inversed_recs, output / "recommendations")
    write_df_per_uid(inversed_recs, gz_output / "recommendations", "group_id")
