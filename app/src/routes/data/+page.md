# data

This page contains scraped and processed data from MangaDex.
The schemas are applicable to the parquet datasets
Minor structural transformations have been applied to make it easier to process that data via PySpark.

## manga

Download link:

- [manga.parquet](/api/v1/data/manga.parquet)
- [manga.ndjson](/api/v1/data/manga.ndjson)

See [MangaDex API documentation for manga](https://api.mangadex.org/docs/docs/manga/).

### schema

<div class="schema">

```
root
 |-- id: string (nullable = true)
 |-- relationships: array (nullable = true)
 |    |-- element: struct (containsNull = true)
 |    |    |-- id: string (nullable = true)
 |    |    |-- related: string (nullable = true)
 |    |    |-- type: string (nullable = true)
 |-- type: string (nullable = true)
 |-- attributes: struct (nullable = true)
 |    |-- availableTranslatedLanguages: array (nullable = true)
 |    |    |-- element: string (containsNull = true)
 |    |-- chapterNumbersResetOnNewVolume: boolean (nullable = true)
 |    |-- contentRating: string (nullable = true)
 |    |-- createdAt: string (nullable = true)
 |    |-- isLocked: boolean (nullable = true)
 |    |-- lastChapter: string (nullable = true)
 |    |-- lastVolume: string (nullable = true)
 |    |-- latestUploadedChapter: string (nullable = true)
 |    |-- originalLanguage: string (nullable = true)
 |    |-- publicationDemographic: string (nullable = true)
 |    |-- state: string (nullable = true)
 |    |-- status: string (nullable = true)
 |    |-- tags: array (nullable = true)
 |    |    |-- element: struct (containsNull = true)
 |    |    |    |-- attributes: struct (nullable = true)
 |    |    |    |    |-- group: string (nullable = true)
 |    |    |    |    |-- name: struct (nullable = true)
 |    |    |    |    |    |-- en: string (nullable = true)
 |    |    |    |    |-- version: long (nullable = true)
 |    |    |    |-- id: string (nullable = true)
 |    |    |    |-- relationships: array (nullable = true)
 |    |    |    |    |-- element: string (containsNull = true)
 |    |    |    |-- type: string (nullable = true)
 |    |-- updatedAt: string (nullable = true)
 |    |-- version: long (nullable = true)
 |    |-- year: long (nullable = true)
 |    |-- altTitles: map (nullable = true)
 |    |    |-- key: string
 |    |    |-- value: string (valueContainsNull = true)
 |    |-- description: map (nullable = true)
 |    |    |-- key: string
 |    |    |-- value: string (valueContainsNull = true)
 |    |-- links: map (nullable = true)
 |    |    |-- key: string
 |    |    |-- value: string (valueContainsNull = true)
 |    |-- title: map (nullable = true)
 |    |    |-- key: string
 |    |    |-- value: string (valueContainsNull = true)
```

</div>

## chapter

Download links:

- [chapter.parquet](/api/v1/data/chapter.parquet)
- [chapter.njson](/api/v1/data/chapter.njson)

See [MangaDex API documentation for chapter](https://api.mangadex.org/docs/docs/chapter/).

### schema

<div class="schema">

```
root
 |-- id: string (nullable = true)
 |    |-- chapter: string (nullable = true)
 |    |-- createdAt: string (nullable = true)
 |    |-- externalUrl: string (nullable = true)
 |    |-- pages: long (nullable = true)
 |    |-- publishAt: string (nullable = true)
 |    |-- readableAt: string (nullable = true)
 |    |-- title: string (nullable = true)
 |    |-- translatedLanguage: string (nullable = true)
 |    |-- updatedAt: string (nullable = true)
 |    |-- version: long (nullable = true)
 |    |-- volume: string (nullable = true)
 |-- type: string (nullable = true)
 |-- relationships: struct (nullable = true)
 |    |-- manga: string (nullable = true)
 |    |-- scanlation_group: string (nullable = true)
 |    |-- user: string (nullable = true)
```

</div>

## group

Download link:

- [group.parquet](/api/v1/data/group.parquet)
- [group.ndjson](/api/v1/data/group.ndjson)

See [MangaDex API documentation for group](https://api.mangadex.org/docs/docs/group/).

### schema

<div class="schema">

```
root
 |-- attributes: struct (nullable = true)
 |    |-- altNames: array (nullable = true)
 |    |    |-- element: struct (containsNull = true)
 |    |    |    |-- en: string (nullable = true)
 |    |-- contactEmail: string (nullable = true)
 |    |-- createdAt: string (nullable = true)
 |    |-- description: string (nullable = true)
 |    |-- discord: string (nullable = true)
 |    |-- focusedLanguages: array (nullable = true)
 |    |    |-- element: string (containsNull = true)
 |    |-- inactive: boolean (nullable = true)
 |    |-- ircChannel: string (nullable = true)
 |    |-- ircServer: string (nullable = true)
 |    |-- locked: boolean (nullable = true)
 |    |-- mangaUpdates: string (nullable = true)
 |    |-- name: string (nullable = true)
 |    |-- official: boolean (nullable = true)
 |    |-- publishDelay: string (nullable = true)
 |    |-- twitter: string (nullable = true)
 |    |-- updatedAt: string (nullable = true)
 |    |-- verified: boolean (nullable = true)
 |    |-- version: long (nullable = true)
 |    |-- website: string (nullable = true)
 |-- id: string (nullable = true)
 |-- relationships: array (nullable = true)
 |    |-- element: struct (containsNull = true)
 |    |    |-- id: string (nullable = true)
 |    |    |-- type: string (nullable = true)
 |-- type: string (nullable = true)
```

</div>

<style>
.schema {
    overflow-x: auto;
}
</style>
