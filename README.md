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
scrapy runspider manga_recsys/scrapy/manga.py -a path=data/raw/2022-12-10-mangadex-uuid.csv -o data/raw/2022-12-10-mangadex-manga.ndjson -t jsonlines

python scripts/estimate_scrape_time.py 65737 data/raw/2022-12-10-mangadex-manga.ndjson --polling-interval 5 --model-interval 15
```

Here's the scraping for all of the chapters

```bash
scrapy runspider manga_recsys/scrapy/chapter.py -a path=data/raw/2022-12-10-mangadex-uuid.csv -o data/raw/2022-12-16-mangadex-chapter.ndjson -t jsonlines -a limit=10

for (;;) { Get-Date -format o; cat data/raw/2022-12-16-mangadex-chapter.ndjson | wc; sleep 30; }
```

And here's scraping for scan groups:

```bash
scrapy runspider manga_recsys/scrapy/group.py -a path=data/processed/2022-12-16-mangadex-chapter.parquet -o data/raw/2022-12-17-mangadex-group.ndjson -t jsonlines -a limit=10
```

### preprocessing

```bash
manga-parquet data/raw/2022-12-10-mangadex-manga.ndjson data/processed/2022-12-10-mangadex-manga
tag-rules data/processed/2022-12-10-mangadex-manga.parquet data/processed/2022-12-14-tag-rules/
chapter-parquet data/raw/2022-12-16-mangadex-chapter.ndjson data/processed/2022-12-16-mangadex-chapter
group-parquet data/raw/2022-12-17-mangadex-group.ndjson data/processed/2022-12-17-mangadex-group
```

````

### storage

```bash
gcloud --project manga-recsys storage buckets create gs://manga-recsys
gsutil -m rsync -r data/ gs://manga-recsys/data/
````

### decompressive transcoding

- https://cloud.google.com/storage/docs/transcoding

The biggest design decision that needs to be handled is how to store all of the recommendations.
I'm planning on storing all of the recommendations as a json file per entity.
The client can directly query for one of these files, and we can simply serve the static content out of cloud storage.
There is room for optimization here though; GCS offers the ability to transcode files on the fly.

For example, we might want to upload all of the files under a particular directory as gzipped content.
When a cloud run instance requests the data, we should try to decompress on the GCS side and serve the content directly.
This is because bandwidth is free within Google Cloud, but CPU is not.
On the other hand, when a user requests the data, we should serve the gzipped content directly.
The browser will decompress the content on the fly, and the user will not notice any difference.

Implementing this is a bit tricky, but it should be possible.
