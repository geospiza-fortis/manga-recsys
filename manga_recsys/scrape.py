import requests
import subprocess
from pathlib import Path
from argparse import ArgumentParser
from math import ceil


def get_total_pages(base_uri: str) -> int:
    r = requests.get(f"{base_uri}/manga?limit=1")
    return r.json()["total"]


def get_manga_list(base_uri: str, offset: int, limit: int) -> list:
    """Get a list of manga, sorted by creation date ascending."""
    r = requests.get(
        f"{base_uri}/manga?offset={offset}&limit={limit}&order%5BcreatedAt%5D=asc"
    )
    # check if the request was successful
    if r.status_code != 200:
        raise Exception(f"Request failed with status code {r.status_code}")
    data = r.json()
    if not data["result"] == "ok":
        raise Exception(f"Request failed: {data}")
    return r.json()["results"]


def parser():
    parser = ArgumentParser()
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--base_uri", type=str, default="https://api.mangadex.org")
    parser.add_argument("--output-path", type=str, default="data/raw/dump")
    return parser.parse_args()


def main():
    args = parser()

    # get the total number of manga
    total = get_total_pages(args.base_uri)

    parts = ceil(total / args.limit)
    print(f"Total number of manga: {total}")
    print(f"Downloading in {parts} with {args.limit} manga per part")


if __name__ == "__main__":
    pass
