"""Generate metadata that maps groups/manga/chapters to their respective ids.

This is useful for traversing the relationships between the different metadata
"""
from pathlib import Path

import click
from pyspark.sql import Window
from pyspark.sql import functions as F

from manga_recsys.commands.utils import write_df, write_df_per_group
from manga_recsys.spark import get_spark


@click.command()
@click.argument("input-group", type=click.Path(exists=True))
@click.argument("input-manga", type=click.Path(exists=True))
@click.argument("input-chapter", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--cores", type=int, default=16)
@click.option("--memory", default="24g")
def metadata_listing(input_group, input_manga, input_chapter, output, cores, memory):
    """Generate metadata that maps groups/manga/chapters to their respective ids.

    This also captures broad relationships between metadata, such as the manga
    that a group has translated.
    """
    spark = get_spark(cores=cores, memory=memory)

    group = spark.read.parquet(input_group)
    manga = spark.read.parquet(input_manga)
    chapter = spark.read.parquet(input_chapter)

    manga_name_lang = manga.select(
        F.col("id").alias("manga_id"),
        F.explode("attributes.title").alias("lang", "manga_name"),
    )

    lang_ordered = (
        manga_name_lang.groupBy("lang")
        .count()
        .orderBy(F.desc("count"))
        .withColumn("rank", F.row_number().over(Window.orderBy(F.desc("count"))))
    )

    # take the language for each manga that has the lowest rank
    manga_name = (
        manga_name_lang.join(lang_ordered, "lang")
        .withColumn(
            "manga_lang_rank",
            F.row_number().over(Window.partitionBy("manga_id").orderBy("rank")),
        )
        .filter(F.col("manga_lang_rank") == 1)
        .select("manga_id", "manga_name", "lang")
    )

    chapter_groups = chapter.select(
        F.col("id").alias("chapter_id"),
        F.col("relationships.scanlation_group").alias("group_id"),
        F.col("relationships.manga").alias("manga_id"),
        F.col("attributes.pages"),
    )

    group_manga = (
        group.select(
            F.col("id").alias("group_id"), F.col("attributes.name").alias("group_name")
        )
        .join(chapter_groups, "group_id")
        .join(manga_name, "manga_id")
    )
    group_manga = (
        group_manga.groupBy(
            *[c for c in group_manga.columns if c not in ["chapter_id", "pages"]]
        )
        .agg(
            F.countDistinct("chapter_id").alias("chapter_count"),
            F.sum("pages").alias("page_count"),
        )
        .orderBy("group_id", "manga_id")
        .cache()
    )

    group_summary = (
        group_manga.groupBy("group_id", "group_name")
        .agg(
            F.countDistinct("manga_id").alias("manga_count"),
            F.sum("chapter_count").alias("total_chapters"),
            F.sum("page_count").alias("total_pages"),
        )
        .orderBy("group_id")
        .cache()
    )

    group_manga.printSchema()
    group_manga.show()
    group_summary.printSchema()
    group_summary.show()

    write_df(group_manga, Path(output) / "group_manga")
    write_df_per_group(group_manga, Path(output) / "group_manga", cores)
    write_df(group_summary, Path(output) / "group_summary")
