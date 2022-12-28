"""Generate recommendations from from manga to manga."""
from pathlib import Path

import click

from manga_recsys.commands.utils import write_df, write_df_per_uid
from manga_recsys.models.manga import (
    explode_recommendations,
    generate_manga_tags_tfidf_lsi,
    generate_manga_tags_word2vec,
    generate_recommendations,
    map_names_to_recommendations,
)
from manga_recsys.spark import get_spark


@click.group()
def manga():
    """Generate manga recommendations."""
    pass


def _write_recs(recs, output, cores=8):
    output = Path(output)
    gz_output = Path("/".join([output.parts[0], "gz", *output.parts[1:]]))
    write_df(recs, output / "recommendations")
    print("Writing gzipped files...")
    write_df_per_uid(
        recs, gz_output / "recommendations", uid_col="id", parallelism=cores
    )


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--num-recs", type=int, default=20)
@click.option("--cores", type=int, default=8)
@click.option("--memory", default="6g")
def tags_word2vec(input_manga_info, output, num_recs, cores, memory):
    """Generate word2vec vectors from tags to make recommendations."""
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    manga_tags = generate_manga_tags_word2vec(
        manga_info, vector_col="w2v", workers=cores
    )
    rec_df = generate_recommendations(
        manga_tags, "id", "w2v", k=num_recs, metric="cosine", n_jobs=cores
    )
    recs = explode_recommendations(spark, rec_df)
    recs = map_names_to_recommendations(manga_info, recs).cache()
    recs.printSchema()
    recs.show()

    _write_recs(recs, output, cores)


@manga.command()
@click.argument("input-manga-info", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--num-recs", type=int, default=20)
@click.option("--cores", type=int, default=8)
@click.option("--memory", default="6g")
def tags_lsi(input_manga_info, output, num_recs, cores, memory):
    spark = get_spark(cores=cores, memory=memory)
    manga_info = spark.read.parquet(input_manga_info).cache()

    # https://radimrehurek.com/gensim/models/lsimodel.html
    manga_tags_lsi, (_, _) = generate_manga_tags_tfidf_lsi(
        manga_info, return_model=True
    )

    rec_df = generate_recommendations(
        manga_tags_lsi, "id", "lsi", k=num_recs, metric="cosine", n_jobs=cores
    )

    recs = explode_recommendations(spark, rec_df)
    recs = map_names_to_recommendations(manga_info, recs).cache()
    recs.printSchema()
    recs.show()

    _write_recs(recs, output, cores)
