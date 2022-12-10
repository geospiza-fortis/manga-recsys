import os
import sys
from argparse import ArgumentParser

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def convert_via_json(col, type):
    # # https://stackoverflow.com/a/70393584
    return F.from_json(F.to_json(col), schema=type)


def combine_maps(list):
    # https://stackoverflow.com/a/43724338
    if not list:
        return None
    return {k: v for m in list for k, v in m.items()}


def mappify_struct(col):
    comb = F.udf(combine_maps, "map<string, string>")
    return comb(convert_via_json(col, "array<map<string, string>>"))


def parse_args():
    """Parse the input path, output path, and spark options."""
    parser = ArgumentParser()
    parser.add_argument("input", help="Input path")
    parser.add_argument("output", help="Output path")
    parser.add_argument("--cores", type=int, default=16)
    parser.add_argument("--memory", default="24g")
    parser.add_argument("--partitions", type=int, default=1)
    return parser.parse_args()


def main():
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    args = parse_args()
    spark = (
        SparkSession.builder.config("spark.driver.memory", args.memory)
        .config("spark.driver.cores", args.cores)
        .config("spark.sql.shuffle.partitions", args.cores * 2)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )

    raw = spark.read.text(args.input)
    df = spark.read.json(raw.rdd.map(lambda r: r.value)).repartition(args.cores * 2)
    cols_to_mappify = ["altTitles", "description", "links", "title"]
    clean = df.select(
        *[c for c in df.columns if c != "attributes"],
        F.struct(
            *[
                F.col(f"attributes.{c}").alias(c)
                for c in df.select("attributes.*").columns
                if c not in cols_to_mappify
            ],
            *[mappify_struct(f"attributes.{c}").alias(c) for c in cols_to_mappify],
        ).alias("attributes"),
    )
    clean.printSchema()
    clean.repartition(args.partitions).write.parquet(args.output)


if __name__ == "__main__":
    main()
