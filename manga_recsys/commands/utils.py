import functools
import shutil
from multiprocessing import Pool
from pathlib import Path

import click
import tqdm
from pyspark.sql import functions as F


def simple_io_options(func):
    @click.option("--cores", default=8, help="Number of cores to use")
    @click.option("--memory", default="6g", help="Amount of memory to use")
    @click.argument("input", type=click.Path(exists=True))
    @click.argument("output", type=click.Path())
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


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


def write_df(df, path):
    path = Path(path)
    df.repartition(1).write.parquet(path.as_posix(), mode="overwrite")
    consolidate_parquet(path)
    df.toPandas().to_json(path.with_suffix(".json"), orient="records", indent=2)


def _write_df_per_uid(pdf, path, uid, uid_col="id"):
    group_df = pdf[pdf[uid_col] == uid]
    group_df.to_json(path / f"{uid}.json", orient="records", indent=2)


def write_df_per_uid(df, path, uid_col, parallelism=8):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    pdf = df.toPandas()
    with Pool(parallelism) as p:
        p.starmap(
            _write_df_per_uid,
            tqdm.tqdm([(pdf, path, uid, uid_col) for uid in pdf[uid_col].unique()]),
        )


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
