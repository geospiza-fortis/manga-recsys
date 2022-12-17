# data

## manga

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

<style>
.schema {
    overflow-x: auto;
}
</style>
