# manga-recsys recommendation

This is a project to build a semi-useful recommendation from mangadex's API.
There are other projects out there; this one is primarily for learning and fun.

## see also

- https://github.com/similar-manga/similar
- https://github.com/CarlosEsco/Neko

## notes

### scraping

A list of all manga uuids (as of 2022-12-10) was graciously provided by tristan9 (thanks!).
If we do need to scrape this from scratch, we filter using the `createdAtSince` parameter and paginate according to limits set by the api.

```bash
# -a limit=10 for testing
scrapy runspider manga_recsys/scrapy/mangadex.py -a path=data/raw/2022-12-10-mangadex-uuid.csv -o data/raw/2022-12-10-mangadex-manga.ndjson -t jsonlines

python scripts/estimate_scrape_time.py 65737 data/raw/2022-12-10-mangadex-manga.ndjson --polling-interval 5 --model-interval 15
```

### preprocessing

```bash
manga-parquet data/raw/2022-12-10-mangadex-manga.ndjson data/processed/2022-12-10-mangadex-manga

tag-rules data/processed/2022-12-10-mangadex-manga.parquet data/processed/2022-12-14-tag-rules/
```

````

### storage

```bash
gcloud --project geospiza storage buckets create gs://manga-recsys
gsutil -m rsync -r data/ gs://manga-recsys/data/
````
