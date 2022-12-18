from pathlib import Path

import click
from pyspark.ml.fpm import FPGrowth
from pyspark.sql import functions as F

from manga_recsys.commands.utils import simple_io_options
from manga_recsys.spark import get_spark


@click.command()
@simple_io_options
def tag_rules(input, output, cores, memory):
    """Generate tag association rules from manga parquet files."""
    spark = get_spark(cores, memory)

    df = spark.read.parquet(input)

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

    # write out parquet and json files (records) for each
    Path(output).mkdir(parents=True, exist_ok=True)
    freq_df = fpm.freqItemsets.toPandas()
    freq_df.to_parquet(f"{output}/freq_itemsets.parquet")
    freq_df.to_json(f"{output}/freq_itemsets.json", orient="records")

    assoc_df = fpm.associationRules.toPandas()
    assoc_df.to_parquet(f"{output}/association_rules.parquet")
    assoc_df.to_json(f"{output}/association_rules.json", orient="records")


if __name__ == "__main__":
    main()
