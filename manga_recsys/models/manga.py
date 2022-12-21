from functools import partial

import numpy as np
import pandas as pd
import pyspark.sql
from gensim.models import Word2Vec
from pynndescent import NNDescent
from pyspark.sql import functions as F


def get_tag_counts(manga_info: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
    """Get the number of manga for each tag."""
    return (
        manga_info.select("id", F.explode("tags").alias("tag"))
        .groupBy("tag.group", "tag.name")
        .agg(F.countDistinct("id").alias("n"))
        .orderBy(F.desc("n"))
    )


def get_manga_tags(manga_info: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
    """Get a list of tags for each manga."""
    return (
        manga_info.select("id", F.explode("tags").alias("tag"))
        .groupBy("id")
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
) -> pd.DataFrame:
    """Create a new dataframe that contains recommendations using NNDescent.

    This will add a recommendations and distances column into a new dataframe.
    """
    # generate an index for nearest neighbor search
    index = NNDescent(np.stack(df[vector_col]), metric=metric, n_jobs=n_jobs)

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
