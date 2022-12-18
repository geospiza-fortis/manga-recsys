import shutil
from argparse import ArgumentParser
from pathlib import Path

from pyspark.sql import functions as F


def parse_parquet_args():
    """Parse the input path, output path, and spark options."""
    parser = ArgumentParser()
    parser.add_argument("input", help="Input path")
    parser.add_argument("output", help="Output path")
    parser.add_argument("--cores", type=int, default=16)
    parser.add_argument("--memory", default="24g")
    return parser.parse_args()


def consolidate_parquet(path):
    """Convert a single partition in a spark directory into a single parquet file
    outside of it."""
    path = Path(path)
    name = f"{path.name}.parquet"
    if (path.parent / name).exists():
        (path.parent / name).unlink()
    source = next(path.glob("*.parquet"))
    shutil.move(source, path.parent / name)
    shutil.rmtree(path)


def convert_via_json(col, type):
    # # https://stackoverflow.com/a/70393584
    return F.from_json(F.to_json(col), schema=type)


def combine_maps(list):
    # https://stackoverflow.com/a/43724338
    if not list:
        return None
    return {k: v for m in list for k, v in m.items()}


def mappify_array_struct(col):
    comb = F.udf(combine_maps, "map<string, string>")
    return comb(convert_via_json(col, "array<map<string, string>>"))


def mappify_struct(col):
    return convert_via_json(col, "map<string, string>")


# convert an array of objects with type and value into a struct
def pivot_relationship(df, pivot_col, id_col="id"):
    """pivot an array of id, type into a struct that contains all the values"""
    pivoted = (
        df.select(id_col, F.explode(pivot_col).alias("pivot"))
        .groupBy(id_col)
        .pivot("pivot.type")
        .agg(F.first("pivot.id"))
    )
    pivoted_nested = pivoted.select(
        id_col,
        F.struct([c for c in pivoted.columns if c != id_col]).alias(pivot_col),
    )
    return df.drop(pivot_col).join(pivoted_nested, on=id_col, how="left")
