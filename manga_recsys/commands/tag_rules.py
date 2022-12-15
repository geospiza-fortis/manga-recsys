from argparse import ArgumentParser
from pathlib import Path

from pyspark.ml.fpm import FPGrowth
from pyspark.sql import functions as F

from manga_recsys.spark import get_spark


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
    return parser.parse_args()


def main():
    args = parse_args()
    spark = get_spark()

    df = spark.read.parquet(args.input)

    exploded_tags = df.select("id", F.explode("attributes.tags").alias("tag")).select(
        F.col("id").alias("manga_id"),
        F.col("tag.attributes.name.en").alias("tag_name"),
        F.col("tag.id").alias("tag_id"),
    )
    collected_tags = exploded_tags.groupBy("manga_id").agg(
        F.collect_set("tag_name").alias("tag_names")
    )

    fp = FPGrowth(
        itemsCol="tag_names",
        predictionCol="prediction",
        minSupport=0.01,
        minConfidence=0.01,
    )
    fpm = fp.fit(collected_tags)

    # write out two parquet files using pandas
    Path(args.output).mkdir(parents=True, exist_ok=True)
    fpm.freqItemsets.toPandas().to_parquet(f"{args.output}/freq_itemsets.parquet")
    fpm.associationRules.toPandas().to_parquet(
        f"{args.output}/association_rules.parquet"
    )


if __name__ == "__main__":
    main()
