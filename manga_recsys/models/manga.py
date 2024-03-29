import gc
import time
from functools import partial
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyspark.sql
import scipy.linalg
import scipy.sparse.linalg
import umap
from gensim import corpora
from gensim.matutils import corpus2dense
from gensim.models import LsiModel, TfidfModel, Word2Vec
from pynndescent import NNDescent
from pyspark.sql import Window
from pyspark.sql import functions as F
from scipy.sparse import csgraph


def get_tag_counts(manga_info: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
    """Get the number of manga for each tag."""
    return (
        manga_info.select("id", F.explode("tags").alias("tag"))
        .groupBy("tag.group", "tag.name")
        .agg(F.countDistinct("id").alias("n"))
        .orderBy(F.desc("n"))
    )


def get_manga_tags(
    manga_info: pyspark.sql.DataFrame, group: Optional[str] = None
) -> pyspark.sql.DataFrame:
    """Get a list of tags for each manga."""
    assert group in ["theme", "format", "genre", "content", None], "Invalid group"
    exploded = manga_info.select("id", F.explode("tags").alias("tag"))
    if group is not None:
        exploded = exploded.filter(F.col("tag.group") == group)
    return (
        exploded.groupBy("id")
        .agg(F.collect_list("tag.name").alias("tags"))
        .orderBy("id")
    )


def average_tag_vectors(model, tags):
    """Given a gensim w2v model and list of tags, return the average vector for
    all tags."""
    return np.mean([model.wv[tag] for tag in tags], axis=0).tolist()


def generate_manga_tags_word2vec(
    manga_info: pyspark.sql.DataFrame,
    vector_col: str = "w2v",
    vector_size: int = 16,
    workers: int = 8,
    return_model: bool = False,
) -> pd.DataFrame:
    """Add an averaged wordvector as a feature to the manga_tags dataframe."""
    manga_tags = get_manga_tags(manga_info).toPandas()

    # generate the word2vec model using cbow
    sentences = [list(x) for x in manga_tags.tags.tolist()]
    tags_model = Word2Vec(sentences, sg=0, vector_size=vector_size, workers=workers)

    # add features to the manga_tags dataframe to start making recommendations
    manga_tags[vector_col] = manga_tags.tags.apply(
        partial(average_tag_vectors, tags_model)
    )
    if return_model:
        return manga_tags, tags_model
    else:
        return manga_tags


def generate_manga_tags_tfidf_lsi(
    manga_info: pyspark.sql.DataFrame,
    vector_col: str = "lsi",
    vector_size: int = 16,
    return_model: bool = False,
) -> pd.DataFrame:
    """Add an averaged wordvector as a feature to the manga_tags dataframe."""
    manga_tags = get_manga_tags(manga_info).toPandas()

    # generate the word2vec model using cbow
    dictionary = corpora.Dictionary(manga_tags.tags)
    corpus = [dictionary.doc2bow(text) for text in manga_tags.tags]
    tfidf = TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    lsi = LsiModel(corpus_tfidf, id2word=dictionary, num_topics=vector_size)

    # add features to the manga_tags dataframe to start making recommendations
    manga_tags[vector_col] = corpus2dense(
        lsi[corpus_tfidf], num_terms=vector_size
    ).T.tolist()
    if return_model:
        return manga_tags, (tfidf, lsi)
    else:
        return manga_tags


def network_deconvolution(G, k=None):
    """Deconvolve a network matrix using the eigen decomposition.
    https://www.nature.com/articles/nbt.2635
    """
    # eigen decomposition
    if k:
        lam, v = scipy.linalg.eigh(G, driver="evr", eigvals=(0, k))
    else:
        lam, v = scipy.linalg.eigh(G, driver="evd")
    # rescale the eigenvalues
    # also add small value to avoid division by zero
    lam_dir = lam / (1 + lam)
    # reconstruct the deconvolved matrix
    G_dir = v @ np.diag(lam_dir) @ v.T

    # remove diagonal, threshold positive values, and rescale in-place
    np.fill_diagonal(G_dir, 0)
    np.maximum(G_dir, 0, out=G_dir)
    G_dir /= np.max(G_dir)

    # NOTE: check reconstruction
    # G_dir = v @ np.diag(lam) @ v.T
    return G_dir


def network_deconvolution_svd(G, k=None):
    """Deconvolve a network matrix using svd pseudo-inverse.
    https://www.nature.com/articles/nbt.2635
    """
    if k is not None:
        u, s, vh = scipy.sparse.linalg.svds(
            G + np.eye(G.shape[0], dtype=np.float32), k=k, which="SM"
        )
    else:
        u, s, vh = scipy.linalg.svd(G + np.eye(G.shape[0], dtype=np.float32))
    G_dir = G @ (u @ np.linalg.pinv(np.diag(s)) @ vh)

    # remove diagonal, threshold positive values, and rescale in-place
    np.fill_diagonal(G_dir, 0)
    np.maximum(G_dir, 0, out=G_dir)
    G_dir /= np.max(G_dir)

    return G_dir


def network_silencing(G):
    """Remove indirect effects using a silencing method.
    https://www.nature.com/articles/nbt.2601
    """
    # svd of G
    u, s, vh = scipy.linalg.svd(G)

    peturb = np.diag((G - np.eye(G.shape[0])) @ G)
    G_dir = (
        (G - np.eye(G.shape[0]) + np.diag(peturb))
        # multiply with pseudo inverse
        @ (u @ np.linalg.pinv(np.diag(s)) @ vh)
    )

    # remove diagonal, threshold positive values, and rescale in-place
    np.fill_diagonal(G_dir, 0)
    np.maximum(G_dir, 0, out=G_dir)
    G_dir /= np.max(G_dir)

    # NOTE: check reconstruction
    # G_dir = u @ np.diag(s) @ vh
    return G_dir


def generate_manga_tags_network(
    manga_info: pyspark.sql.DataFrame,
    vector_col: str = "network",
    vector_size: int = 256,
    deconvolve: bool = False,
    solve_k: int = None,
    laplacian: bool = True,
    metric: str = "cosine",
    output_metric: str = "euclidean",
    **kwargs,
) -> pd.DataFrame:
    """Add an averaged word vector as a feature to the manga_tags dataframe."""
    manga_tags = get_manga_tags(manga_info).toPandas()

    # generate the network model using cbow
    dictionary = corpora.Dictionary(manga_tags.tags)
    corpus = [dictionary.doc2bow(tags) for tags in manga_tags.tags]

    # time sections
    start = time.time()
    print("generating manga-manga matrix")
    tag_manga_mat = corpus2dense(corpus, num_terms=len(dictionary), dtype=np.float32)
    manga_manga_mat = tag_manga_mat.T @ tag_manga_mat
    # if dense
    np.fill_diagonal(manga_manga_mat, 0)
    # fill diagonal of csc matrix with zeros
    # manga_manga_mat.setdiag(0)
    print(f"generated manga-manga matrix: {time.time() - start:.2f} seconds")

    if deconvolve:
        # this returns a real matrix, but entries might be negative due to
        # rescaling. does this pose a problem when computing the laplacian?
        print("deconvolving matrix")
        start = time.time()
        # play around with k to see how it affects the results
        tmp_deconvolved = network_deconvolution(manga_manga_mat, k=solve_k)
        del manga_manga_mat
        manga_manga_mat = tmp_deconvolved
        print(f"deconvolved matrix: {time.time() - start:.2f} seconds")

    if laplacian:
        print("computing laplacian")
        start = time.time()
        csgraph.laplacian(manga_manga_mat, normed=True, copy=False)
        print(f"computing laplacian: {time.time() - start:.2f} seconds")

    # convert this back into a sparse matrix
    manga_manga_mat = np.asarray(manga_manga_mat)

    # force garbage collection; does this do anything?
    gc.collect()

    # generate an embedding using umap, which is reasonably fast
    # we force the output metric to be the same as the input metric, which
    # makes downstream computations theoretically sound.
    print("generating embedding")
    start = time.time()
    reducer = umap.UMAP(
        n_components=vector_size,
        metric=metric,
        output_metric=output_metric,
        low_memory=True,
        verbose=True,
    )
    emb = reducer.fit_transform(manga_manga_mat)
    print(f"generated embedding: {time.time() - start:.2f} seconds")

    # free up some memory before copying the embedding
    del manga_manga_mat

    # add features to the manga_tags dataframe to start making recommendations
    manga_tags[vector_col] = emb.tolist()

    return manga_tags


def get_closest(index, mapping, k, query_vector):
    indices, distances = index.query([query_vector], k=k)
    return mapping[indices[0]].tolist(), distances[0].tolist()


def generate_recommendations(
    df: pd.DataFrame,
    id_col: str,
    vector_col: str,
    k: int = 10,
    metric: int = "cosine",
    n_jobs: int = 8,
    verbose: bool = True,
    low_memory: bool = False,
) -> pd.DataFrame:
    """Create a new dataframe that contains recommendations using NNDescent.

    This will add a recommendations and distances column into a new dataframe.
    """
    # generate an index for nearest neighbor search
    index = NNDescent(
        np.stack(df[vector_col]),
        metric=metric,
        n_jobs=n_jobs,
        verbose=verbose,
        low_memory=low_memory,
    )

    # create recommendations using a mapping to get the original ids
    rec_series = df[vector_col].apply(partial(get_closest, index, df[id_col], k))

    # generate a new dataframe with the recommendations
    rec_df = pd.DataFrame(rec_series.tolist(), columns=["recommendations", "distances"])
    return pd.concat([df, rec_df], axis=1)


def explode_recommendations(
    spark: pyspark.sql.SparkSession, df: pd.DataFrame
) -> pyspark.sql.DataFrame:
    """Explode the recommendations and distances columns into their own rows.

    Returns a PySpark DataFrame that contains id, rec_id, and distance.
    """
    return (
        spark.createDataFrame(df)
        .withColumn(
            "rec", F.explode(F.arrays_zip(F.col("recommendations"), F.col("distances")))
        )
        .select("id", "rec.*")
        .orderBy("id", "distances")
        .withColumnRenamed("recommendations", "rec_id")
        .withColumnRenamed("distances", "distance")
    )


def map_names_to_recommendations(
    manga_info: pyspark.sql.DataFrame,
    recommendations: pyspark.sql.DataFrame,
) -> pyspark.sql.DataFrame:
    """Map the manga names to the recommendations."""
    id_name = manga_info.select("id", "name")
    return (
        recommendations.join(id_name, on="id", how="left")
        .join(
            id_name.select(
                F.col("id").alias("rec_id"), F.col("name").alias("rec_name")
            ),
            on="rec_id",
            how="left",
        )
        .select("id", "name", "rec_id", "rec_name", "distance")
        .orderBy("id", "distance")
    )


# keep only manga that contains the following tag
def recs_with_secondary_tag(
    spark: pyspark.sql.SparkSession,
    recs: pd.DataFrame,
    manga_tags: pyspark.sql.DataFrame,
    primary_tag: str,
    k_tags: int = 5,
    pre_filter_primary: bool = True,
    post_filter_primary: bool = True,
    verbose: bool = True,
):
    """Get a secondary tag based on the tags of the neighbors.

    Optionally filter down the recommendations to only include manga that have
    the primary tag.
    """

    if pre_filter_primary:
        recs = (
            spark.createDataFrame(recs)
            .where(F.array_contains("tags", primary_tag))
            .toPandas()
        )

    # get the most common tag from each neighbor
    # this is a type of belief propagation algorithm
    tag_mode = (
        explode_recommendations(spark, recs)
        .join(
            manga_tags.select("id", "tags").withColumnRenamed("id", "rec_id"),
            on="rec_id",
            how="inner",
        )
        .withColumn("tag", F.explode("tags"))
        .groupBy("id", "tag")
        .count()
        .where(F.col("tag") != primary_tag)
        # now keep the most common tag for each manga
        .withColumn(
            "rank",
            F.rank().over(
                Window.partitionBy("id").orderBy(F.col("count").desc(), F.col("tag"))
            ),
        )
        .where(F.col("rank") == 1)
        .drop("rank")
        # now only keep rows that have a primary tag
    )

    # keep the top 5 tags, otherwise label it as "other"
    top_tags = (
        tag_mode.groupBy("tag")
        .count()
        .orderBy(F.col("count").desc())
        .limit(k_tags)
        .drop("count")
        .withColumn("common", F.lit(True))
    )

    tag_common = (
        tag_mode.join(top_tags, on="tag", how="left")
        .fillna(False, subset=["common"])
        .withColumn("tag", F.when(F.col("common"), F.col("tag")).otherwise("Other"))
        .drop("common")
    )

    df = spark.createDataFrame(recs).join(tag_common, on="id", how="left")
    if post_filter_primary:
        df = df.where(F.array_contains("tags", primary_tag))

    if verbose:
        df.groupBy("tag").count().orderBy(F.col("count").desc()).show(n=10)
        df.show(n=5)
        print("final count", df.count())
    return df.toPandas()


def plot_recommendation_dims(df, vector_col, reducer, title, n_dims=2, sample=None):
    if sample is not None:
        df = df.sample(sample)
    vec = reducer.fit_transform(np.stack(df[vector_col]))

    # add color map for the tag using convention
    tag_freq = df.groupby("tag").count().sort_values("id", ascending=False)
    color_map = {tag: f"C{i}" for i, tag in enumerate(tag_freq.index)}

    # scatter in either 2 or 3 dimensions
    _, ax = plt.subplots(figsize=(8, 8))
    if n_dims == 2:
        ax.scatter(
            *[vec[:, i] for i in range(n_dims)],
            c=df.tag.fillna("Other").apply(color_map.get),
            # tens of thousands of small dots, so use alpha to make it look better
            alpha=0.5,
        )
    elif n_dims == 3:
        ax = plt.axes(projection="3d")
        ax.scatter3D(
            *[vec[:, i] for i in range(n_dims)],
            c=df.tag.fillna("Other").apply(color_map.get),
            # tens of thousands of small dots, so use alpha to make it look better
            alpha=0.5,
        )
    else:
        raise ValueError("n_dims must be 2 or 3")

    # add legend
    for tag, color in color_map.items():
        ax.scatter([], [], c=color, label=tag)

    ax.set_title(title)
    ax.legend(loc="upper right", title="Secondary Tag")

    plt.tight_layout()
