# manga-recsys recommendation

This is a project to build a semi-useful recommendation from mangadex's API.
There are other projects out there; this one is primarily for learning and fun.

## see also

- https://github.com/similar-manga/similar
- https://github.com/CarlosEsco/Neko

## quickstart

To get started, copy the `.env.example` file to `.env` and fill in the appropriate values.
If you do not have a copy of the data directory, you can set the nginx container to serve static files from the cloud bucket.

Use the `docker compose` stack to run the application.

```bash
docker compose up
```

### testing openapi

The openapi spec is found at [app/static/openapi](app/static/openapi).

The spec is rendered via redoc on http://localhost:5173/openapi.
A separate instance of redoc is available on http://localhost:4001.
On platforms other than Windows, the standalone redoc instance should provide hot-reloading.

Use [schemathesis](https://github.com/schemathesis/schemathesis) to test the openapi spec.
If you are simply developing against the production service, you can use the following command without any dependencies:

```bash
st run --checks all https://manga-recsys.geospiza.me/openapi/openapi.yaml --base-url https://manga-recsys.geospiza.me
```

If you are developing locally, use the following command:

```bash
st run --checks all http://localhost:5173/openapi/openapi.yaml --base-url http://localhost:5173
```

## notes

### scraping

A list of all manga uuids (as of 2022-12-10) was graciously provided by tristan9 (thanks!).
If we do need to scrape this from scratch, we filter using the `createdAtSince` parameter and paginate according to limits set by the api.

```bash
#  for testing
scrapy runspider manga_recsys/scrapy/manga.py -a path=data/raw/2022-12-10-mangadex-uuid.csv -o data/raw/2022-12-10-mangadex-manga.ndjson -t jsonlines -a limit=10

scrapy runspider manga_recsys/scrapy/chapter.py -a path=data/raw/2022-12-10-mangadex-uuid.csv -o data/raw/2022-12-16-mangadex-chapter.ndjson -t jsonlines -a limit=10

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

# second manga recommendations based on tag lsi
manga-recsys models manga tags-lsi data/processed/2022-12-17-metadata-listing/manga_info.parquet data/processed/2022-12-27-recommendation-manga-tags-lsi

# recommendation based on tag network
manga-recsys models manga tags-network data/processed/2022-12-17-metadata-listing/manga_info.parquet data/processed/2022-12-28-recommendation-manga-tags-network


# plots for manga recommendations
manga-recsys models manga plot-models data/processed/2022-12-17-metadata-listing/manga_info.parquet data/processed/2022-12-27-recommendation-manga-plots

manga-recsys models manga generate-plot-manifest data/processed/2022-12-27-recommendation-manga-plots
```

### storage

```bash
gcloud --project manga-recsys storage buckets create gs://manga-recsys
manga-recsys sync tar-gz
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
