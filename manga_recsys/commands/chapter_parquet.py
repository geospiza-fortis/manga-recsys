from argparse import ArgumentParser

from manga_recsys.commands.utils import consolidate_parquet, pivot_relationship
from manga_recsys.spark import get_spark


def parse_args():
    """Parse the input path, output path, and spark options."""
    parser = ArgumentParser()
    parser.add_argument("input", help="Input path")
    parser.add_argument("output", help="Output path")
    parser.add_argument("--cores", type=int, default=16)
    parser.add_argument("--memory", default="24g")
    return parser.parse_args()


def main():
    args = parse_args()
    spark = get_spark(cores=args.cores, memory=args.memory)
    df = spark.read.json(args.input)
    df = pivot_relationship(df, "relationships")
    df.printSchema()
    df.repartition(1).write.parquet(args.output, mode="overwrite")
    consolidate_parquet(args.output)


if __name__ == "__main__":
    main()
