import click
from pyspark.sql import functions as F

from manga_recsys.commands.utils import (
    consolidate_parquet,
    mappify_array_struct,
    mappify_struct,
    pivot_relationship,
    simple_io_options,
)
from manga_recsys.spark import get_spark


@click.group(name="parquet")
def parquet():
    """Convert JSON ndjson API responses to parquet files via PySpark."""
    pass


@parquet.command()
@simple_io_options
def chapter(input, output, cores, memory):
    """Convert chapter JSON to parquet."""
    spark = get_spark(cores, memory)
    df = spark.read.json(input)
    df = pivot_relationship(df, "relationships")
    df.printSchema()
    df.repartition(1).write.parquet(output, mode="overwrite")
    consolidate_parquet(output)


@parquet.command()
@simple_io_options
def group(input, output, cores, memory):
    """Convert group JSON to parquet."""
    spark = get_spark(cores, memory)
    df = spark.read.json(input)
    df.printSchema()
    df.repartition(1).write.parquet(output, mode="overwrite")
    consolidate_parquet(output)


@parquet.command()
@simple_io_options
def manga(input, output, cores, memory):
    """Convert manga JSON to parquet."""
    spark = get_spark(cores, memory)

    raw = spark.read.text(input)
    df = spark.read.json(raw.rdd.map(lambda r: r.value)).repartition(cores * 2)
    cols_to_mappify = ["description", "links", "title"]
    clean = df.select(
        *[c for c in df.columns if c != "attributes"],
        F.struct(
            *[
                F.col(f"attributes.{c}").alias(c)
                for c in df.select("attributes.*").columns
                if c not in cols_to_mappify + ["altTitles"]
            ],
            mappify_array_struct(f"attributes.altTitles").alias("altTitles"),
            *[mappify_struct(f"attributes.{c}").alias(c) for c in cols_to_mappify],
        ).alias("attributes"),
    )
    clean.printSchema()
    clean.repartition(1).write.parquet(output, mode="overwrite")
    consolidate_parquet(output)
