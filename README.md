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
manga-recsys parquet manga data/raw/2022-12-10-mangadex-manga.ndjson data/processed/2022-12-10-mangadex-manga
manga-recsys parquet chapter data/raw/2022-12-16-mangadex-chapter.ndjson data/processed/2022-12-16-mangadex-chapter
manga-recsys parquet group data/raw/2022-12-17-mangadex-group.ndjson data/processed/2022-12-17-mangadex-group

manga-recsys metadata data/processed/2022-12-17-mangadex-group.parquet data/processed/2022-12-10-mangadex-manga.parquet data/processed/2022-12-16-mangadex-chapter.parquet data/processed/2022-12-17-metadata-listing
```

### modeling

```bash
manga-recsys models tag-rules data/processed/2022-12-10-mangadex-manga.parquet data/processed/2022-12-14-tag-rules

# original model, page count rating
manga-recsys models group-manga data/processed/2022-12-16-mangadex-chapter.parquet data/processed/2022-12-17-metadata-listing/group_manga.parquet data/processed/2022-12-18-recommendation-group-manga

# log-count rating
manga-recsys models group-manga data/processed/2022-12-16-mangadex-chapter.parquet data/processed/2022-12-17-metadata-listing/group_manga.parquet data/processed/2022-12-19-recommendation-group-manga

# first manga recommendations based on tag word2vec
manga-recsys models manga tags-word2vec data/processed/2022-12-17-metadata-listing/manga_info.parquet data/processed/2022-12-20-recommendation-manga-tags-word2vec
```

### storage

```bash
gcloud --project manga-recsys storage buckets create gs://manga-recsys
manga-recsys sync upload
# for small static files that are directly downloaded by clients, to help save on bandwidth
manga-recsys sync upload-gz
manga-recsys sync download
```

### decompressive transcoding

- https://cloud.google.com/storage/docs/transcoding
- https://stackoverflow.com/questions/31170100/gsutil-rsync-with-gzip-compression

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

### model comparisons

Here's one method for objectively comparing two recommendation models.
We get the results of all neighbors to a given manga, with (node, recommendation) pairs.
We do this for each model.
Then we compute the jaccard similarity between the two sets of recommendations.
We can test this against a null model by randomly shuffling pairs.
