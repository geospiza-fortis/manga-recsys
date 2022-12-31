# first manga recommendations based on tag word2vec
manga-recsys models manga tags-word2vec `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-20-recommendation-manga-tags-word2vec

# second manga recommendations based on tag lsi
manga-recsys models manga tags-lsi `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-27-recommendation-manga-tags-lsi

#--------------------------------------------------------------------------------
# plots
#--------------------------------------------------------------------------------

manga-recsys models manga plot-models `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-20-recommendation-manga-tags-word2vec/embedding.parquet `
    word2vec data/processed/2022-12-27-recommendation-manga-plots

manga-recsys models manga plot-models `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-27-recommendation-manga-tags-lsi/embedding.parquet `
    lsi data/processed/2022-12-27-recommendation-manga-plots
