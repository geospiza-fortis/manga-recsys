"""Generate metadata that maps groups/manga/chapters to their respective ids.

This is useful for traversing the relationships between the different metadata
"""
from pathlib import Path

import click
from pyspark.sql import Window
from pyspark.sql import functions as F

from manga_recsys.commands.utils import write_df, write_df_per_uid
from manga_recsys.spark import get_spark


@click.command()
@click.argument("input-group", type=click.Path(exists=True))
@click.argument("input-manga", type=click.Path(exists=True))
@click.argument("input-chapter", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--cores", type=int, default=16)
@click.option("--memory", default="24g")
def metadata(input_group, input_manga, input_chapter, output, cores, memory):
    """Generate metadata that maps groups/manga/chapters to their respective ids.

    This also captures broad relationships between metadata, such as the manga
    that a group has translated.
    """
    spark = get_spark(cores=cores, memory=memory)

    group = spark.read.parquet(input_group).cache()
    manga = spark.read.parquet(input_manga).cache()
    chapter = spark.read.parquet(input_chapter).cache()

    manga_name_lang = manga.select(
        F.col("id").alias("manga_id"),
        F.explode("attributes.title").alias("lang", "manga_name"),
    )

    manga_description_lang = manga.select(
        F.col("id").alias("manga_id"),
        F.explode("attributes.description").alias("lang", "manga_description"),
    )

    lang_ordered = (
        manga_name_lang.groupBy("lang")
        .count()
        .orderBy(F.desc("count"))
        .withColumn("rank", F.row_number().over(Window.orderBy(F.desc("count"))))
    )

    # take the language for each manga that has the lowest rank
    manga_name_description = (
        manga_name_lang.join(manga_description_lang, ["manga_id", "lang"])
        .join(lang_ordered, "lang")
        .withColumn(
            "manga_lang_rank",
            F.row_number().over(Window.partitionBy("manga_id").orderBy("rank")),
        )
        .filter(F.col("manga_lang_rank") == 1)
        .select("manga_id", "manga_name", "manga_description", "lang")
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
        .join(manga_name_description.drop("manga_description"), "manga_id")
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
    ).cache()

    group_summary = (
        group_manga.groupBy("group_id", "group_name")
        .agg(
            F.countDistinct("manga_id").alias("manga_count"),
            F.sum("chapter_count").alias("total_chapters"),
            F.sum("page_count").alias("total_pages"),
        )
        .orderBy("group_id")
    ).cache()

    # now lets also process info for groups and manga separately

    manga_tags = (
        manga.select("id", F.explode("attributes.tags").alias("tag"))
        .select(
            "id",
            F.struct(
                "tag.attributes.group",
                F.col("tag.attributes.name.en").alias("name"),
            ).alias("tag"),
        )
        .groupBy("id")
        .agg(F.collect_list("tag").alias("tags"))
    )

    manga_info = (
        manga.select(
            "id",
            "attributes.createdAt",
            "attributes.updatedAt",
            "attributes.availableTranslatedLanguages",
            "attributes.originalLanguage",
            "attributes.publicationDemographic",
            "attributes.status",
            "attributes.year",
            "attributes.contentRating",
        )
        .join(
            group_manga.select(
                F.col("manga_id").alias("id"),
                F.col("manga_name").alias("name"),
                "chapter_count",
                "page_count",
            ),
            "id",
        )
        .join(
            manga_name_description.select(
                F.col("manga_id").alias("id"),
                F.col("manga_description").alias("description"),
            ),
            "id",
        )
        .join(manga_tags, "id")
    )

    group_info = group.select(
        "id",
        "attributes.name",
        "attributes.createdAt",
        "attributes.updatedAt",
        "attributes.description",
        "attributes.inactive",
    )

    group_manga.printSchema()
    group_manga.show()
    group_summary.printSchema()
    group_summary.show()

    group_info.printSchema()
    group_info.show()
    manga_info.printSchema()
    manga_info.show()

    write_df(group_manga, Path(output) / "group_manga")
    write_df_per_uid(group_manga, Path(output) / "group_manga", "group_id", cores)
    write_df(group_summary, Path(output) / "group_summary")

    write_df(group_info, Path(output) / "group_info")
    write_df_per_uid(group_info, Path(output) / "group_info", "id", cores)
    write_df(manga_info, Path(output) / "manga_info")
    write_df_per_uid(manga_info, Path(output) / "manga_info", "id", cores)
