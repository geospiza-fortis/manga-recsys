# defaults: laplacian embedding with 256 dimensions, euclidean distance, no deconvolution

#--------------------------------------------------------------------------------
# network-cosine
#--------------------------------------------------------------------------------

# NOTE: this metric is not theoretically justified on the graph laplacian
manga-recsys models manga tags-network `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-cosine `
    --metric cosine

manga-recsys models manga plot-models `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-cosine/embedding.parquet `
    network-cosine data/processed/2022-12-27-recommendation-manga-plots

#--------------------------------------------------------------------------------
# network-wasserstein
#--------------------------------------------------------------------------------

# NOTE: this doesn't work because UMAP doesn't support this metric
# manga-recsys models manga tags-network `
#     data/processed/2022-12-17-metadata-listing/manga_info.parquet `
#     data/processed/2022-12-28-recommendation-manga-tags-network-wasserstein `
#     --metric wasserstein

#--------------------------------------------------------------------------------
# network-euclidean
#--------------------------------------------------------------------------------

manga-recsys models manga tags-network `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-euclidean `
    --metric euclidean

manga-recsys models manga plot-models `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-euclidean/embedding.parquet `
    network-euclidean data/processed/2022-12-27-recommendation-manga-plots

#--------------------------------------------------------------------------------
# network-adj-cosine
#--------------------------------------------------------------------------------

manga-recsys models manga tags-network `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-adj-cosine `
    --metric cosine --no-laplacian

manga-recsys models manga plot-models `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-adj-cosine/embedding.parquet `
    network-adj-cosine data/processed/2022-12-27-recommendation-manga-plots

#--------------------------------------------------------------------------------
# network-deconv-euclidean
#--------------------------------------------------------------------------------

manga-recsys models manga tags-network `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-deconv-euclidean `
    --metric euclidean --laplacian --deconvolve

manga-recsys models manga plot-models `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-deconv-euclidean/embedding.parquet `
    network-deconv-euclidean data/processed/2022-12-27-recommendation-manga-plots

#--------------------------------------------------------------------------------
# network-deconv-adj-cosine
#--------------------------------------------------------------------------------

manga-recsys models manga tags-network `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-deconv-adj-cosine `
    --metric cosine --no-laplacian --vector-size 128 --deconvolve

manga-recsys models manga plot-models `
    data/processed/2022-12-17-metadata-listing/manga_info.parquet `
    data/processed/2022-12-28-recommendation-manga-tags-network-deconv-adj-cosine/embedding.parquet `
    network-deconv-adj-cosine data/processed/2022-12-27-recommendation-manga-plots
