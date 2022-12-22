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


def tar_big_directories(root, output, threshold=100, parallelism=8):
    """We tarball directories that have more than 100 files and copy this into a
    separate directory.

    We'll need to create an inverse of this function in order to actually deploy
    on the cloud.
    """
    directories_to_tar = []
    for path in root.glob("**/"):
        if path.is_file():
            continue
        if len(list(path.glob("*"))) > threshold:
            directories_to_tar.append(path)

    # now create the set of files to copy over as-is
    files_to_copy = []
    for path in root.glob("**/*"):
        if path.is_dir():
            continue
        if path.parent not in directories_to_tar:
            files_to_copy.append(path)

    # in parallel, tar the directories into the output directory
    print("tarring directories")
    with Pool(parallelism) as p:
        p.starmap(
            shutil.make_archive,
            tqdm.tqdm(
                [
                    (
                        (output / p.relative_to(root)).as_posix(),
                        "tar",
                        p.as_posix(),
                    )
                    for p in directories_to_tar
                ],
                total=len(directories_to_tar),
            ),
        )

    # now in parallel, copy the files into the output directory
    print("copying files")
    # first make all the directories that dont exist
    for p in files_to_copy:
        (output / p.relative_to(root)).parent.mkdir(parents=True, exist_ok=True)
    with Pool(parallelism) as p:
        p.starmap(
            shutil.copy,
            tqdm.tqdm(
                [
                    (p.as_posix(), (output / p.relative_to(root)).as_posix())
                    for p in files_to_copy
                ],
                total=len(files_to_copy),
            ),
        )


def untar_big_directories(root, output, parallelism=8):
    """Untar the directories that were tarred in the root directory into the
    output directory.
    """
    # first, untar the directories
    tar_paths = [p for p in root.glob("**/*.tar")]
    with Pool(parallelism) as p:
        p.starmap(
            shutil.unpack_archive,
            # make sure to create a new directory with the tarball name
            tqdm.tqdm(
                [
                    (
                        p.as_posix(),
                        (
                            output / p.relative_to(root).as_posix().replace(".tar", "")
                        ).as_posix(),
                    )
                    for p in tar_paths
                ],
                total=len(tar_paths),
            ),
        )
    other_paths = [p for p in root.glob("**/*") if p not in tar_paths]
    with Pool(parallelism) as p:
        p.starmap(
            shutil.copy,
            tqdm.tqdm(
                [
                    (p.as_posix(), (output / p.relative_to(root)).as_posix())
                    for p in other_paths
                ],
                total=len(other_paths),
            ),
        )


def gzip_file(input_path, output_path):
    """Compress a file using Python's gzip module."""
    # ensure output path exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(input_path, "rb") as f_in:
        with gzip.open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def _compress_data(data_root, overwrite=True, cores=8):
    should_compress = [
        p for p in data_root.glob("**/*.json") if p.parts[1] not in ["gz", "tar"]
    ]
    if not overwrite:
        should_compress = [
            p
            for p in should_compress
            if not (data_root / "gz" / p.relative_to(data_root)).exists()
        ]
    with Pool(cores) as p:
        p.starmap(
            gzip_file,
            tqdm.tqdm(
                [
                    (
                        p.as_posix(),
                        (data_root / "gz" / p.relative_to(data_root)).as_posix(),
                    )
                    for p in should_compress
                ]
            ),
        )


@click.group()
def sync():
    """Synchronize local data with the remote storage bucket."""
    pass


@sync.command()
@click.option("--cores", default=8, help="Number of cores to use during compression")
def tar_gz(cores):
    """Create a tar directory of the gz folder. Must be untarred to be synced."""
    _compress_data(Path("data/"), True, cores)
    tar_big_directories(Path("data/gz"), Path("data/tar"), parallelism=cores)


@sync.command()
@click.option("--output", default="data/gz", help="Output directory for gz files")
@click.option("--cores", default=8, help="Number of cores to use during compression")
def untar_gz(output, cores):
    """Untar the gz folder."""
    # exit early if gz folder already exists
    if Path(output).exists():
        return
    untar_big_directories(Path("data/tar"), Path(output), parallelism=cores)


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

    _compress_data(input_path, overwrite, cores)
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
        check=True,
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
        subprocess.run(cmd, shell=True, check=True)


@sync.command()
@click.option("--path", default="data/", help="Path to local data directory")
def download(path):
    """Download remote data to the local storage bucket."""
    assert path.endswith("/"), "path must end with a slash"
    assert path.startswith("data/"), "path must start with data/"
    assert Path(path).exists(), "data directory not found"
    cmd = [
        "gsutil",
        "-m",
        "rsync",
        "-x",
        "'^gz'",
        "-r",
        f"gs://manga-recsys/{path}",
        f"{path}",
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, shell=True, check=True)
