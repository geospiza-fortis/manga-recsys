"""Synchronize local data with the remote storage bucket.

We shell out to the command-line tools for this, since all of the logic is
implemented for multi-processing, partial uploads, and differential syncs. Here,
the main thing we need to figure out is how to handle files that need to be
served compressed.

- https://cloud.google.com/storage/docs/transcoding
- https://stackoverflow.com/questions/31170100/gsutil-rsync-with-gzip-compression
"""

import gzip
import shutil
import subprocess
from multiprocessing import Pool
from pathlib import Path

import click
import tqdm


def gzip_file(input_path, output_path):
    """Compress a file using Python's gzip module."""
    # ensure output path exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(input_path, "rb") as f_in:
        with gzip.open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


@click.group()
def sync():
    """Synchronize local data with the remote storage bucket."""
    pass


@sync.command()
@click.option(
    "--overwrite/--no-overwrite", default=False, help="Overwrite existing files"
)
@click.option("--delete/--no-delete", default=False, help="Delete remote files")
@click.option("--cores", default=8, help="Number of cores to use during compression")
def upload_gz(overwrite, delete, cores):
    """Compress and upload files that need to be served compressed."""

    input_path = Path("data/")
    assert input_path.exists() and input_path.is_dir(), "data directory not found"

    # compress json files that are smaller than 10mb
    should_compress = [
        p
        for p in input_path.glob("**/*.json")
        if p.parts[1] != "gz" and p.stat().st_size < 10_000_000
    ]
    if not overwrite:
        should_compress = [
            p
            for p in should_compress
            if not (input_path / "gz" / p.relative_to(input_path)).exists()
        ]
    with Pool(cores) as p:
        p.starmap(
            gzip_file,
            tqdm.tqdm(
                [
                    (
                        p.as_posix(),
                        (input_path / "gz" / p.relative_to(input_path)).as_posix(),
                    )
                    for p in should_compress
                ]
            ),
        )
    subprocess.run(
        [
            "gsutil",
            "-m",
            "-h",
            "content-encoding:gzip",
            "rsync",
            *(["-d"] if delete else []),
            "-r",
            "data/gz/",
            "gs://manga-recsys/data/gz/",
        ],
        shell=True,
    )


@sync.command()
@click.option("--delete/--no-delete", default=False, help="Delete remote files")
def upload(delete):
    """Upload local data to the remote storage bucket."""
    root = Path("data/")
    assert root.exists(), "data directory not found"
    # TODO: we assume that we do not store small individual files in the
    # processed folder, and instead write them directly into the gz folder. This
    # is a bit hacky, but we avoid unnecessary strife trying to upload new files
    # into gcs. We skip the gz folder because its contents are uploaded
    # separately.
    for path in root.glob("*"):
        if path.is_file():
            print("warning: found file in data directory", path)
            continue
        if path.name == "gz":
            continue
        cmd = [
            "gsutil",
            "-m",
            "rsync",
            *(["-d"] if delete else []),
            "-r",
            f"{path.as_posix()}/",
            f"gs://manga-recsys/{path.as_posix()}/",
        ]
        print(" ".join(cmd))
        subprocess.run(cmd, shell=True)


@sync.command()
def download():
    """Download remote data to the local storage bucket."""
    assert Path("data/").exists(), "data directory not found"
    cmd = [
        "gsutil",
        "-m",
        "rsync",
        "-x",
        "^gz",
        "-r",
        "gs://manga-recsys/data/",
        "data/",
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, shell=True)
