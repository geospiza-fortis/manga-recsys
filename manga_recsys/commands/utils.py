import functools
import gzip
import json
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


def _consolidate(path, file_ext):
    path = Path(path)
    name = f"{path.name}.{file_ext}"
    if (path.parent / name).exists():
        (path.parent / name).unlink()
    source = next(path.glob(f"*.{file_ext}"))
    shutil.move(source, path.parent / name)
    shutil.rmtree(path)


def consolidate_parquet(path):
    """Convert a single partition in a spark directory into a single parquet file
    outside of it."""
    _consolidate(path, "parquet")


def consolidate_json(path):
    """Convert a single partition in a spark directory into a single json file
    outside of it."""
    _consolidate(path, "json")


def write_df(df, path):
    path = Path(path)
    parted = df.repartition(1).cache()
    parted.write.parquet(path.as_posix(), mode="overwrite")
    consolidate_parquet(path)
    collected = [row.asDict(recursive=True) for row in parted.collect()]
    path.with_suffix(".json").write_text(json.dumps(collected))
    parted.unpersist()


def _write_df_per_uid(rows, path, uid, uid_col, compress):
    d = [row.asDict(recursive=True) for row in rows if row[uid_col] == uid]
    uid = d[0][uid_col]
    json_data = json.dumps(d)
    # write gzip to disk
    out = Path(path / f"{uid}.json")
    if compress:
        out.write_bytes(gzip.compress(json_data.encode()))
    else:
        out.write_text(json_data)


def write_df_per_uid(df, path, uid_col, compress=True, parallelism=8):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    rows = df.collect()
    unique_uids = set([row[uid_col] for row in rows])
    with Pool(parallelism) as p:
        p.starmap(
            _write_df_per_uid,
            tqdm.tqdm([(rows, path, uid, uid_col, compress) for uid in unique_uids]),
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
