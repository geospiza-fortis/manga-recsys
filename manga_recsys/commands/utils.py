import functools
import gzip
import json
import shutil
from multiprocessing import Pool
from pathlib import Path

import click
import ndjson
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


def write_df(df, path, write_json=True):
    path = Path(path)
    print(f"Writing to {path}")
    parted = df.repartition(1).cache()
    parted.write.parquet(path.as_posix(), mode="overwrite")
    consolidate_parquet(path)
    if write_json:
        collected = [row.asDict(recursive=True) for row in parted.collect()]
        path.with_suffix(".json").write_text(json.dumps(collected))
    parted.unpersist()


def _rewrite_spark_json_partition(path, compress):
    # parse the uid column from the pathname
    uid_col, uid = path.parts[-2].split("=")
    rows = ndjson.loads(path.read_text(encoding="utf-8"))
    rows = [{uid_col: uid, **row} for row in rows]
    json_data = json.dumps(rows)
    # write gzip to disk
    out = Path(path.parent.parent / f"{uid}.json")
    if compress:
        out.write_bytes(gzip.compress(json_data.encode()))
    else:
        out.write_text(json_data)


def write_df_per_uid(df, path, uid_col, compress=True, parallelism=8):
    path = Path(path)
    print(f"Writing to {path}")
    path.mkdir(parents=True, exist_ok=True)
    # write by partition to disk, include index column
    df.repartition(uid_col).write.partitionBy(uid_col).json(
        path.as_posix(), mode="overwrite"
    )
    # now move all these files up a level into the main directory
    paths = [p for p in path.glob("*/*.json")]
    with Pool(parallelism) as p:
        list(
            tqdm.tqdm(
                p.imap(
                    functools.partial(
                        _rewrite_spark_json_partition,
                        compress=compress,
                    ),
                    paths,
                ),
                total=len(paths),
            )
        )

    # now remove all of the partition directories
    directories = [p for p in path.glob("*") if p.is_dir()]
    with Pool(parallelism) as p:
        list(tqdm.tqdm(p.imap(shutil.rmtree, directories), total=len(directories)))

    # also delete success files
    for p in [p for p in path.glob("*") if not p.name.endswith(".json")]:
        p.unlink()


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
