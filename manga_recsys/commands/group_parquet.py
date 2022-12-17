from manga_recsys.commands.utils import consolidate_parquet, parse_parquet_args
from manga_recsys.spark import get_spark


def main():
    args = parse_parquet_args()
    spark = get_spark(cores=args.cores, memory=args.memory)
    df = spark.read.json(args.input)
    df.printSchema()
    df.repartition(1).write.parquet(args.output, mode="overwrite")
    consolidate_parquet(args.output)


if __name__ == "__main__":
    main()
