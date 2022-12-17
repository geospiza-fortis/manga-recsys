from pyspark.sql import functions as F

from manga_recsys.commands.utils import (
    consolidate_parquet,
    mappify_struct,
    parse_parquet_args,
)
from manga_recsys.spark import get_spark


def main():
    args = parse_parquet_args()
    spark = get_spark(cores=args.cores, memory=args.memory)

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
    clean.repartition(1).write.parquet(args.output, mode="overwrite")
    consolidate_parquet(args.output)


if __name__ == "__main__":
    main()
