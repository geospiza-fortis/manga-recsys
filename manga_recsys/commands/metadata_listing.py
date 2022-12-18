"""Generate metadata that maps groups/manga/chapters to their respective ids.

This is useful for traversing the relationships between the different metadata
"""
from argparse import ArgumentParser
from pathlib import Path

import tqdm
from pyspark.sql import Window
from pyspark.sql import functions as F

from manga_recsys.commands.utils import consolidate_parquet
from manga_recsys.spark import get_spark


def parse_args():
    """Parse the input path, output path, and spark options."""
    parser = ArgumentParser()
    parser.add_argument("input_group", help="Input path for group metadata")
    parser.add_argument("input_manga", help="Input path for manga metadata")
    parser.add_argument("input_chapter", help="Input path for chapter metadata")
    parser.add_argument("output", help="Output path")
    parser.add_argument("--cores", type=int, default=16)
    parser.add_argument("--memory", default="24g")
    return parser.parse_args()


def write_df(df, path):
    path = Path(path)
    df.repartition(1).write.parquet(path.as_posix(), mode="overwrite")
    consolidate_parquet(path)
    df.toPandas().to_json(path.with_suffix(".json"), orient="records", indent=2)


def write_df_per_group(df, path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    pdf = df.toPandas()
    # TODO: can be done in parallel
    for group_id in tqdm.tqdm(pdf.group_id.unique()):
        group_df = pdf[pdf.group_id == group_id]
        group_df.to_json(path / f"{group_id}.json", orient="records", indent=2)


def main():
    args = parse_args()
    spark = get_spark(cores=args.cores, memory=args.memory)

    group = spark.read.parquet(args.input_group)
    manga = spark.read.parquet(args.input_manga)
    chapter = spark.read.parquet(args.input_chapter)

    manga_name_lang = manga.select(
        F.col("id").alias("manga_id"),
        F.explode("attributes.title").alias("lang", "name"),
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
        .select("manga_id", "name", "lang")
    )

    chapter_groups = chapter.select(
        F.col("id").alias("chapter_id"),
        F.col("relationships.scanlation_group").alias("group_id"),
        F.col("relationships.manga").alias("manga_id"),
    )

    group_manga = (
        group.select(
            F.col("id").alias("group_id"), F.col("attributes.name").alias("group_name")
        )
        .join(chapter_groups, "group_id")
        .join(manga_name, "manga_id")
    )
    group_manga = (
        group_manga.groupBy(*[c for c in group_manga.columns if c != "chapter_id"])
        .agg(F.countDistinct("chapter_id").alias("chapter_count"))
        .cache()
    )

    group_summary = (
        group_manga.groupBy("group_id", "group_name")
        .agg(
            F.countDistinct("manga_id").alias("manga_count"),
            F.sum("chapter_count").alias("total_chapters"),
        )
        .cache()
    )

    group_manga.printSchema()
    group_summary.printSchema()

    write_df(group_manga, Path(args.output) / "group_manga")
    write_df(group_summary, Path(args.output) / "group_summary")
    write_df_per_group(group_manga, Path(args.output) / "group_summary")


if __name__ == "__main__":
    main()
